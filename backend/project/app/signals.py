import os
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import File
from pathlib import Path


# Signal handler for copying files to the host
@receiver(post_save, sender=File)
def copy_file_to_host(sender, instance, **kwargs):
    if instance.to_host:  # Check if the flag is set
        # Construct the directory path
        project_name = instance.project.name
        repo_path = f'/app/repos/{project_name}'
        os.makedirs(repo_path, exist_ok=True)  # Ensure the directory exists


        # Construct the full file path
        file_path = os.path.join(repo_path, instance.file_path)
        # Ensure the directory for the file exists
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        logging.info(f"Coping file {os.path.basename(instance.file_path)} to {file_path}")
        # Write the file content to the file path
        with open(file_path, 'w') as file:
            file.write(instance.content)
