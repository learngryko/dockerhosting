from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import File
from project.settings import FLASK_SYNC_URL
import requests


@receiver(post_save, sender=File)
def notify_Flask_on_file_change(sender, instance, **kwargs):
    """
    Signal to notify Flask when a file changes. Sends a request to the Flask container
    to sync the latest files for the related project.
    """
    project_id = instance.project.name
    try:
        # Sending a POST request to notify Flask
        requests.post(f"{FLASK_SYNC_URL}/sync-files", json={"project_id": project_id})
        print(f"Notified Flask to sync files for project {project_id}")
    except requests.RequestException as e:
        print(f"Failed to notify Flask: {e}")
