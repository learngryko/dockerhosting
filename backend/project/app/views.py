import os
import git
import shutil  # for deleting the repo folder
import logging
import json
import docker
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from .models import Project, File, Container, Environment
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view


# Set up a logger
logger = logging.getLogger(__name__)

class CloneRepositoryView(APIView):
    def post(self, request):
        try:
            data = request.data  # Use request.data in DRF
            repository_url = data.get('repository_url')
            project_name = data.get('project_name')
            project_description = data.get('description', '')
            build_file_path = data.get('build_file_path', 'NOT SET')

            if not project_name or not repository_url:
                return Response({'status': 'error', 'message': 'Project name and repository URL are required.'}, status=status.HTTP_400_BAD_REQUEST)

            repo_dir = os.path.join(settings.BASE_DIR, 'repositories', project_name)
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            os.makedirs(repo_dir)

            git.Repo.clone_from(repository_url, repo_dir)

            project = Project.objects.create(
                name=project_name,
                description=project_description.replace('\0', ''),
                repository_url=repository_url,
                build_file_path=build_file_path
            )

            for root, dirs, files in os.walk(repo_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_dir)
                    _, file_extension = os.path.splitext(file)

                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().replace('\0', '')

                    File.objects.create(
                        project=project,
                        file_path=relative_path,
                        content=content,
                        extension=file_extension
                    )

            shutil.rmtree(repo_dir)
            return Response({'status': 'success', 'message': 'Project and files created successfully.'}, status=status.HTTP_201_CREATED)

        except git.exc.GitError as e:
            logger.error(f"Git error: {str(e)}")
            return Response({'status': 'error', 'message': f'Git error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListFilesView(APIView):
    def get(self, request, project_name):
        try:
            project = Project.objects.get(name=project_name)
            files = File.objects.filter(project=project)

            files_list = [{'file_path': file.file_path, 'extension': file.extension} for file in files]
            return Response({'status': 'success', 'files': files_list}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)


class FileContentView(APIView):
    def get(self, request, project_name, file_path):
        try:
            project = Project.objects.get(name=project_name)
            file = File.objects.get(project=project, file_path=file_path)
            return Response({'status': 'success', 'content': file.content}, status=status.HTTP_200_OK)
        except (Project.DoesNotExist, File.DoesNotExist):
            return Response({'status': 'error', 'message': 'Project or file not found'}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request, project_name, file_path):
        try:
            project = Project.objects.get(name=project_name)
            file = File.objects.get(project=project, file_path=file_path)
            data = request.data
            new_content = data.get('content', '')
            file.content = new_content
            file.save(update_fields=['content'])
            return Response({'status': 'success', 'message': 'File updated successfully.'}, status=status.HTTP_200_OK)
        except (Project.DoesNotExist, File.DoesNotExist):
            return Response({'status': 'error', 'message': 'Project or file not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class CreateContainerView(APIView):
    def post(self, request):
        try:
            data = request.data
            project_name = data.get('project_name')
            build_file_path = data.get('build_file_path', 'Dockerfile')
            port = data.get('port', 8080)

            project = Project.objects.get(name=project_name)
            client = docker.DockerClient(base_url=settings.DIND_URL)

            build_context_path = f"/app/repos/{project_name}"
            dockerfile_path = f"{build_context_path}/{build_file_path}"

            image, build_logs = client.images.build(
                path=build_context_path,
                dockerfile=build_file_path,
                tag=f"{project_name}_image"
            )

            for log in build_logs:
                logger.info(log)

            container = client.containers.run(
                image=f"{project_name}_image",
                ports={f"{port}/tcp": port},
                detach=True,
                name=f"{project_name}_container"
            )

            return Response({
                'status': 'success',
                'container_id': container.id,
                'message': 'Container created successfully.'
            }, status=status.HTTP_201_CREATED)

        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return Response({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ListContainersView(APIView):
    def get(self, request, project_name=None):
        try:
            if project_name:
                project = Project.objects.get(name=project_name)
                containers = Container.objects.filter(project=project)
            else:
                containers = Container.objects.all()

            container_list = [
                {
                    'container_id': container.container_id,
                    'project': container.project.name,
                    'status': container.status,
                    'port': container.port
                } for container in containers
            ]

            return Response({'status': 'success', 'containers': container_list}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class StartContainerView(APIView):
    def post(self, request, container_id):
        if not container_id:
            return Response({'status': 'error', 'message': 'Container ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Set up Docker client
            client = docker.DockerClient(base_url=settings.DIND_URL)
            container = client.containers.get(container_id)
            container.start()

            # Update the container status in the database
            container_obj = Container.objects.get(container_id=container_id)
            container_obj.status = 'running'
            container_obj.save()

            return Response({'status': 'success', 'message': f'Container {container_id} started successfully.'}, status=status.HTTP_200_OK)
        
        except Container.DoesNotExist:
            return Response({'status': 'error', 'message': 'Container not found.'}, status=status.HTTP_404_NOT_FOUND)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return Response({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StopContainerView(APIView):
    def post(self, request, container_id):
        if not container_id:
            return Response({'status': 'error', 'message': 'Container ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Set up Docker client
            client = docker.DockerClient(base_url=settings.DIND_URL)
            container = client.containers.get(container_id)
            container.stop()

            # Update the container status in the database
            container_obj = Container.objects.get(container_id=container_id)
            container_obj.status = 'stopped'
            container_obj.save()

            return Response({'status': 'success', 'message': f'Container {container_id} stopped successfully.'}, status=status.HTTP_200_OK)
        
        except Container.DoesNotExist:
            return Response({'status': 'error', 'message': 'Container not found.'}, status=status.HTTP_404_NOT_FOUND)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return Response({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SetToHostFlagView(APIView):
    def post(self, request, project_name, flag_value):
        try:
            # Retrieve the project by name
            project = Project.objects.get(name=project_name)

            # Convert the flag_value to a boolean
            if flag_value.lower() == 'true':
                flag = True
            elif flag_value.lower() == 'false':
                flag = False
            else:
                return Response({'status': 'error', 'message': 'Invalid flag value. Use "true" or "false".'}, status=status.HTTP_400_BAD_REQUEST)

            # Update the `to_host` flag for all files related to this project
            File.objects.filter(project=project).update(to_host=flag)

            # Define the project directory path
            project_dir = os.path.join('/app/repos', project_name)

            if flag:
                if not os.path.exists(project_dir):
                    os.makedirs(project_dir)

                files = File.objects.filter(project=project)
                for file in files:
                    file_path = os.path.join(project_dir, file.file_path)
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(file.content)

                logger.info(f"All files for project {project_name} have been downloaded to {project_dir}.")
            else:
                if os.path.exists(project_dir):
                    shutil.rmtree(project_dir)
                    logger.info(f"Project directory {project_dir} has been deleted.")

            return Response({'status': 'success', 'message': f'to_host flag set to {flag} for all files in project {project_name}.'}, status=status.HTTP_200_OK)
        
        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
