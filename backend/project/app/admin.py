# admin.py

from django.contrib import admin
from .models import Project, Environment, File, Container
from django.contrib import messages
from django.utils.translation import ngettext
import os
import shutil
import git
from django.conf import settings
from django.db import transaction
import logging
import subprocess

# Configure logging
logger = logging.getLogger(__name__)

def clone_repository(repo_url, repo_dir):
    """
    Clones a Git repository with real-time progress logging.
    Forces Git to show progress even when not attached to a TTY.
    """
    # Prepare environment so Git will flush progress lines immediately
    env = os.environ.copy()
    env["GIT_FLUSH"] = "1"

    # Remove the directory if it exists, then recreate it
    if os.path.exists(repo_dir):
        shutil.rmtree(repo_dir)
    os.makedirs(repo_dir)

    command = [
        "git", "clone",
        "--progress",    # Force progress messages
        "--verbose",     # More verbose logging
        repo_url,
        repo_dir
    ]

    # Start subprocess with line-buffered text mode
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,    # Typically not much here unless --verbose
        stderr=subprocess.PIPE,    # Git usually sends progress to stderr
        text=True,
        bufsize=1,
        env=env
    )

    # Read and forward logs in real-time
    for line in process.stderr:
        logger.info(line.strip())

    # Wait for the process to complete
    return_code = process.wait()
    if return_code != 0:
        raise Exception(f"Git clone failed with return code {return_code}")

    logger.info("Repository cloned successfully.")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username')

    def save_model(self, request, obj, form, change):
        # Only perform cloning on creation (not on edit)
        if not change:
            repo_dir = os.path.join(settings.BASE_DIR, 'temp_repo', obj.name)
            try:
                with transaction.atomic():  # Ensure atomicity
                    # Save the Project object first
                    super().save_model(request, obj, form, change)

                    logger.info(f"Cloning repository from {obj.repository_url} into {repo_dir}")
                    # Clone with real-time progress
                    clone_repository(obj.repository_url, repo_dir)

                    files_created = 0  # Counter for created files

                    # Walk through the cloned repository and create File objects
                    for root, dirs, files in os.walk(repo_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, repo_dir)
                            _, file_extension = os.path.splitext(file)

                            # Read file content
                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read().replace('\0', '')
                            except Exception as read_err:
                                logger.warning(f"Skipping file '{relative_path}': {read_err}")
                                continue  # Skip files that cannot be read as text

                            # Create File object in the database
                            try:
                                File.objects.create(
                                    project=obj,
                                    file_path=relative_path,
                                    content=content,
                                    extension=file_extension
                                )
                                files_created += 1
                                logger.debug(f"File '{relative_path}' created successfully.")
                            except Exception as db_err:
                                logger.error(f"Failed to create File object for '{relative_path}': {db_err}")

                    # Clean up by removing the cloned repository directory
                    shutil.rmtree(repo_dir)
                    logger.debug(f"Repository directory '{repo_dir}' removed after processing.")

                    # Provide feedback in Django admin
                    messages.success(request, f'Project "{obj.name}" and {files_created} associated files created successfully.')
                    logger.info(f'Project "{obj.name}" created with {files_created} files.')

            except git.exc.GitError as e:
                messages.error(request, f'Git error: {str(e)}')
                logger.error(f"Git error while cloning repository for project '{obj.name}': {e}")
                # Cleanup in case of Git error
                if os.path.exists(repo_dir):
                    shutil.rmtree(repo_dir)
                raise
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                logger.error(f"Error during creation of project '{obj.name}': {e}")
                # Cleanup in case of any other error
                if os.path.exists(repo_dir):
                    shutil.rmtree(repo_dir)
                raise

        else:
            # For edits/changes, simply save the Project instance
            super().save_model(request, obj, form, change)

# Register other models without duplication
admin.site.register(Environment)
admin.site.register(File)
admin.site.register(Container)
