from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import File
from project.settings import DIND_SYNC_URL
import requests


@receiver(post_save, sender=File)
def notify_dind_on_file_change(sender, instance, **kwargs):
    """
    Signal to notify DinD when a file changes. Sends a request to the DinD container
    to sync the latest files for the related project.
    """
    project_id = instance.project.id
    try:
        # Sending a POST request to notify DinD
        requests.post(f"{DIND_SYNC_URL}/sync-files", json={"project_id": project_id})
        print(f"Notified DinD to sync files for project {project_id}")
    except requests.RequestException as e:
        print(f"Failed to notify DinD: {e}")
