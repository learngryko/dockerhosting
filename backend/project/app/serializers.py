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
        fields = '__all__'  # Serialize all fields

class EnvironmentSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)  # Nested project serializer

    class Meta:
        model = Environment
        fields = '__all__'

class FileSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = File
        fields = '__all__' 

class ContainerSerializer(serializers.ModelSerializer):
    project = ProjectSerializer(read_only=True)

    class Meta:
        model = Container
        fields = '__all__'
