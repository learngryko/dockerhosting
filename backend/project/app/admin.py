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

# Configure logging
logger = logging.getLogger(__name__)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username')
    
    def save_model(self, request, obj, form, change):
        if not change:  # Only perform cloning on creation
            repo_dir = os.path.join(settings.BASE_DIR, 'repositories', obj.name)
            try:
                with transaction.atomic():  # Ensure atomicity
                    # First, save the Project instance
                    super().save_model(request, obj, form, change)
                    logger.debug(f'Project "{obj.name}" saved successfully.')

                    # Prepare the repository directory
                    if os.path.exists(repo_dir):
                        shutil.rmtree(repo_dir)
                        logger.debug(f"Existing repository directory '{repo_dir}' removed.")
                    os.makedirs(repo_dir)
                    logger.debug(f"Repository directory '{repo_dir}' created.")

                    # Clone the repository
                    logger.debug(f"Cloning repository from {obj.repository_url} into {repo_dir}")
                    git.Repo.clone_from(obj.repository_url, repo_dir)
                    logger.info(f"Repository cloned successfully for project '{obj.name}'.")

                    files_created = 0  # Counter for created files

                    # Walk through the cloned repository to create File objects
                    for root, dirs, files in os.walk(repo_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            relative_path = os.path.relpath(file_path, repo_dir)
                            _, file_extension = os.path.splitext(file)

                            try:
                                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read().replace('\0', '')
                            except Exception as read_err:
                                logger.warning(f"Skipping file '{relative_path}': {read_err}")
                                continue  # Skip files that can't be read as text

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

                    # Provide feedback to the admin user
                    messages.success(request, f'Project "{obj.name}" and {files_created} associated files created successfully.')
                    logger.info(f'Project "{obj.name}" created with {files_created} files.')

            except git.exc.GitError as e:
                messages.error(request, f'Git error: {str(e)}')
                logger.error(f"Git error while cloning repository for project '{obj.name}': {e}")
                raise
            except Exception as e:
                messages.error(request, f'An error occurred: {str(e)}')
                logger.error(f"Error during creation of project '{obj.name}': {e}")
                if os.path.exists(repo_dir):
                    shutil.rmtree(repo_dir)
                    logger.debug(f"Repository directory '{repo_dir}' removed due to error.")
                raise
        else:
            # For edits/changes, simply save the Project instance
            super().save_model(request, obj, form, change)

# Register other models without duplication
admin.site.register(Environment)
admin.site.register(File)
admin.site.register(Container)
