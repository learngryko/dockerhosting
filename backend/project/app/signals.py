import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import File
from pathlib import Path


@receiver(post_save, sender=File)
def copy_file_to_host(sender, instance, **kwargs):
    project_name = instance.project.name
    repo_path = f'/app/repos/{project_name}'
    file_path = os.path.join(repo_path, instance.file_path)

    if instance.to_host:
        # Ensure the directory exists
        os.makedirs(repo_path, exist_ok=True)
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)

        logging.info(f"Copying file {os.path.basename(instance.file_path)} to {file_path}")

        # Write the file content
        with open(file_path, 'w') as file:
            file.write(instance.content)
    else:
        # Delete file if exists
        if os.path.exists(file_path):
            os.remove(file_path)
            logging.info(f"Deleted file {file_path} as 'to_host' was set to False.")
        else:
            logging.info(f"File {file_path} not found, skipping deletion.")
