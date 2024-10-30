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

# Set up a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class CloneRepositoryView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            repository_url = data.get('repository_url')
            project_name = data.get('project_name')
            project_description = data.get('description', '')

            # Ensure project_name and repository_url are provided
            if not project_name or not repository_url:
                return JsonResponse({'status': 'error', 'message': 'Project name and repository URL are required.'})

            repo_dir = os.path.join(settings.BASE_DIR, 'repositories', project_name)
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)  # Delete the directory if it exists
            os.makedirs(repo_dir)

            git.Repo.clone_from(repository_url, repo_dir)

            project = Project.objects.create(
                name=project_name,
                description=project_description.replace('\0', ''),  # Remove NUL bytes from description
                repository_url=repository_url
            )

            for root, dirs, files in os.walk(repo_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, repo_dir)
                    _, file_extension = os.path.splitext(file)

                    # Read file content, filter out NUL bytes
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().replace('\0', '')  # Remove NUL bytes

                    File.objects.create(
                        project=project,
                        file_path=relative_path,
                        content=content,
                        extension=file_extension
                    )

            shutil.rmtree(repo_dir)  # Clean up after storing files
            return JsonResponse({'status': 'success', 'message': 'Project and files created successfully.'})

        except git.exc.GitError as e:
            logger.error(f"Git error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Git error: {str(e)}'})
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid JSON format.'})
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            # Cleanup: Delete the repository directory after storing files
            if os.path.exists(repo_dir):
                shutil.rmtree(repo_dir)
                logger.info(f"Repository directory {repo_dir} has been deleted after processing.")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'})

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ListFilesView(View):
    def get(self, request, project_name):
        try:
            # Get the project by name
            project = Project.objects.get(name=project_name)
            
            # Fetch all files related to this project
            files = File.objects.filter(project=project)

            # Build a response structure with file paths
            files_list = [{'file_path': file.file_path, 'extension': file.extension} for file in files]
            return JsonResponse({'status': 'success', 'files': files_list}, status=200)
        except Project.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class FileContentView(View):
    def get(self, request, project_name, file_path):
        try:
            # Get the project by name
            project = Project.objects.get(name=project_name)
            
            # Fetch the specific file by its path
            file = File.objects.get(project=project, file_path=file_path)

            # Return the file content
            return JsonResponse({'status': 'success', 'content': file.content}, status=200)
        except (Project.DoesNotExist, File.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Project or file not found'}, status=404)
    
    def post(self, request, project_name, file_path):
        try:
            # Get the project by name
            project = Project.objects.get(name=project_name)
            
            # Fetch the specific file by its path
            file = File.objects.get(project=project, file_path=file_path)

            # Get the new content from the request
            data = json.loads(request.body)
            new_content = data.get('content', '')

            # Update the file content
            file.content = new_content
            file.save()

            return JsonResponse({'status': 'success', 'message': 'File updated successfully.'}, status=200)
        except (Project.DoesNotExist, File.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Project or file not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
        
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CSRFTokenView(View):
    def get(self, request):
        csrf_token = get_token(request)  # Get the CSRF token
        return JsonResponse({'csrfToken': csrf_token})
    
@method_decorator(ensure_csrf_cookie, name='dispatch')
class CreateContainerView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            project_name = data.get('project_name')
            port = data.get('port', 2375)  # Default port

            logger.info(f"Creating containers for project: {project_name}")

            # Get the project by name
            project = Project.objects.get(name=project_name)

            # Set up Docker client
            client = docker.DockerClient(base_url=settings.DIND_URL)

            # Retrieve the build file path from the project
            build_file_path = project.build_file_path
            repo_dir = os.path.join(settings.BASE_DIR, 'repositories', project_name)
            os.makedirs(repo_dir, exist_ok=True)

            # Ensure a valid build file is set
            if not build_file_path or build_file_path == 'NOT SET':
                return JsonResponse({'status': 'error', 'message': 'Build file path is not set.'}, status=400)

            # Fetch the build file from the database
            build_file = File.objects.filter(project=project, file_path=build_file_path).first()
            

            # Check if the build file exists
            if not build_file:
                return JsonResponse({'status': 'error', 'message': f'Build file {build_file_path} not found.'}, status=404)

            # Write the build file to disk  
            build_file_content = build_file.content
            build_file_path_on_disk = os.path.join(repo_dir, os.path.basename(build_file_path))
            with open(build_file_path_on_disk, 'w') as f:
                f.write(build_file_content)

            # Retrieve environment variables and resource limits (if any)
            environment = Environment.objects.filter(project=project).first()
            env_vars = environment.env_vars if environment else {}
            resource_limits = environment.resource_limits if environment else {}

            # Prepare resource limit settings for Docker container (e.g., CPU and memory)
            cpu_limit = resource_limits.get('cpu', None)
            mem_limit = resource_limits.get('memory', None)

            # If the build file is a Dockerfile, build and run the container
            if 'Dockerfile' in build_file_path:
                # Build the Docker image
                image, logs = client.images.build(
                    path=repo_dir,
                    dockerfile=os.path.basename(build_file_path),
                    tag=f"{project_name}_image"
                )

                # Run the container with environment variables and resource limits
                container = client.containers.run(
                    image=f"{project_name}_image",
                    name=f"{project_name}_container",
                    ports={f'{port}/tcp': port},
                    detach=True,
                    environment=env_vars,
                    cpu_quota=int(float(cpu_limit) * 100000) if cpu_limit else None,
                    mem_limit=mem_limit,
                    volumes={f'/path/to/project/{project_name}': {'bind': '/app', 'mode': 'rw'}}  # Bind mount
                )

            # If the build file is a docker-compose.yml, use docker-compose to create containers
            elif 'docker-compose.yml' in build_file_path:
                # Write a modified docker-compose.yml with environment and resource limits, if needed
                compose_path_on_disk = build_file_path_on_disk

                # Assuming docker-compose.yml includes necessary env vars; you could modify it dynamically here
                os.system(f"docker-compose -f {compose_path_on_disk} up -d")

                return JsonResponse({'status': 'success', 'message': 'docker-compose used to create containers.'}, status=201)

            else:
                return JsonResponse({'status': 'error', 'message': 'Invalid build file. Only Dockerfile or docker-compose.yml supported.'}, status=400)

            # Save container details in the database
            container_entry = Container.objects.create(
                project=project,
                container_id=container.id,
                status=container.status,
                port=port
            )
            logger.info(f"Container created succesfully for project: {project_name}")
            # Clean up repo directory after use
            shutil.rmtree(repo_dir)


            return JsonResponse({'status': 'success', 'container_id': container.id, 'message': 'Container created successfully.'}, status=201)

        except Project.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)

@method_decorator(ensure_csrf_cookie, name='dispatch')
class ListContainersView(View):
    def get(self, request, project_name=None):
        try:
            # If project_name is provided, filter by project
            if project_name:
                project = Project.objects.get(name=project_name)
                containers = Container.objects.filter(project=project)
            else:
                # If no project_name is provided, list all containers
                containers = Container.objects.all()

            # Build the response data
            container_list = []
            for container in containers:
                container_list.append({
                    'container_id': container.container_id,
                    'project': container.project.name,
                    'status': container.status,
                    'port': container.port
                })

            return JsonResponse({'status': 'success', 'containers': container_list}, status=200)

        except Project.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class StartContainerView(View):
    def post(self, request, container_id):
        try:
            # Ensure container_id is provided
            if not container_id:
                return JsonResponse({'status': 'error', 'message': 'Container ID is required.'}, status=400)

            # Set up Docker client
            client = docker.DockerClient(base_url=settings.DIND_URL)

            # Get the container
            container = client.containers.get(container_id)

            # Start the container
            container.start()

            # Update the container status in the database
            container_obj = Container.objects.get(container_id=container_id)
            container_obj.status = 'running'
            container_obj.save()

            return JsonResponse({'status': 'success', 'message': f'Container {container_id} started successfully.'}, status=200)

        except Container.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Container not found.'}, status=404)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class StopContainerView(View):
    def post(self, request, container_id):
        try:
            # Ensure container_id is provided
            if not container_id:
                return JsonResponse({'status': 'error', 'message': 'Container ID is required.'}, status=400)

            # Set up Docker client
            client = docker.DockerClient(base_url=settings.DIND_URL)

            # Get the container
            container = client.containers.get(container_id)

            # Stop the container
            container.stop()

            # Update the container status in the database
            container_obj = Container.objects.get(container_id=container_id)
            container_obj.status = 'stopped'
            container_obj.save()

            return JsonResponse({'status': 'success', 'message': f'Container {container_id} stopped successfully.'}, status=200)

        except Container.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Container not found.'}, status=404)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=500)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)


class ProjectFilesSyncView(View):
    def get(self, request, project_name):
        try:
            # Retrieve the project by name
            project = Project.objects.get(name=project_name)

            # Gather all files related to this project
            files = File.objects.filter(project=project)

            # Build a list of file details including paths and content
            files_data = [
                {
                    'file_path': file.file_path,
                    'content': file.content,
                    'extension': file.extension,
                    'updated_at': file.updated_at.isoformat()
                }
                for file in files
            ]

            return JsonResponse({'status': 'success', 'files': files_data}, status=200)

        except Project.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Project not found'}, status=404)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=500)
