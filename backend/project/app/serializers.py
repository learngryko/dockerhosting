# serializers.py
from rest_framework import serializers
from .models import Project, Environment, File, Container

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'  # This will serialize all fields in the Project model

class EnvironmentSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # Nested serializer to show project details

    class Meta:
        model = Environment
        fields = '__all__'  # Serialize all fields in the Environment model

class FileSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # Nested serializer to show project details

    class Meta:
        model = File
        fields = '__all__'  # Serialize all fields in the File model

class ContainerSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # Nested serializer to show project details

    class Meta:
        model = Container
        fields = '__all__'  # Serialize all fields in the Container model
