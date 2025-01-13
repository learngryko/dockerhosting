# serializers.py

from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Project, Environment, File, Container

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']  # Expose necessary fields

class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)  # Include user details

    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'repository_url', 'build_file_path', 'owner', 'created_at', 'updated_at']


class EnvironmentSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # Nested project serializer

    class Meta:
        model = Environment
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = File
        fields = ['id', 'project', 'file_path', 'content', 'extension', 'to_host', 'created_at', 'updated_at'] 

class ContainerSerializer(serializers.ModelSerializer):
    project = serializers.CharField(source='project.name', read_only=True)

    class Meta:
        model = Container
        fields = ['id', 'container_id', 'status', 'port', 'created_at', 'updated_at', 'project']
