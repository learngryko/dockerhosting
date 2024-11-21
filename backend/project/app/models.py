from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    repository_url = models.URLField()  # URL of the repository
    build_file_path = models.CharField(max_length=255, default='NOT SET')  # Path to Dockerfile / docker compose
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')

    def __str__(self):
        return self.name



class Environment(models.Model):
    project = models.ForeignKey(Project, related_name='environments', on_delete=models.CASCADE)
    env_vars = models.JSONField()  # Store environment variables as JSON
    resource_limits = models.JSONField()  # e.g., {"cpu": "2", "memory": "512m"}
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Environment for {self.project.name}"

class File(models.Model):
    project = models.ForeignKey(Project, related_name='files', on_delete=models.CASCADE)
    file_path = models.CharField(max_length=255)  # Path of the file in the repo
    content = models.TextField()  # Code content of the file
    extension = models.TextField()
    to_host = models.BooleanField(default=False)  # New flag to trigger copying to host
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.file_path


class Container(models.Model):
    project = models.ForeignKey(Project, related_name='containers', on_delete=models.CASCADE)
    container_id = models.CharField(max_length=255)  # Docker container ID
    status = models.CharField(max_length=50)  # e.g., 'running', 'stopped'
    port = models.IntegerField()  # Port the container is running on
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Container {self.container_id} for {self.project.name}"
