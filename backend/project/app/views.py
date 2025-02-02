import os
import git
import shutil  # for deleting the repo folder
import logging
import docker
import requests


from django.conf import settings
from .models import Project, File, Container
from .serializers import ProjectSerializer, ContainerSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.http import StreamingHttpResponse

logger = logging.getLogger(__name__)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Logout successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CloneRepositoryView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        repo_dir = None
        try:
            data = request.data
            repository_url = data.get('repository_url')
            project_name = data.get('project_name')
            project_description = data.get('description', '')
            build_file_path = data.get('build_file_path', 'NOT SET')

            if not project_name or not repository_url:
                logger.error("Project name and repository URL are required.")
                return Response({'status': 'error', 'message': 'Project name and repository URL are required.'}, status=status.HTTP_400_BAD_REQUEST)

            repo_dir = os.path.join(settings.BASE_DIR, 'temp_repo', project_name)

            if os.path.exists(repo_dir):
                logger.info(f"Removing existing directory: {repo_dir}")
                shutil.rmtree(repo_dir)

            logger.info(f"Creating directory for repository: {repo_dir}")
            os.makedirs(repo_dir)

            logger.info(f"Starting clone from {repository_url} to {repo_dir}")

            def progress_callback(op_code, cur_count, max_count, message):
                percent_complete = (cur_count / max_count) * 100 if max_count else 0
                logger.info(f"Cloning progress: {percent_complete:.2f}% complete")

            repo = git.Repo.clone_from(repository_url, repo_dir, progress=progress_callback)
            logger.info("Repository cloned successfully.")

            project = Project.objects.create(
                name=project_name,
                description=project_description.replace('\0', ''),
                repository_url=repository_url,
                build_file_path=build_file_path,
                owner=request.user
            )
            logger.info(f"Project {project_name} created successfully.")

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
            logger.info(f"Files for project {project_name} created successfully.")

            shutil.rmtree(repo_dir)
            logger.info(f"Temporary repository directory {repo_dir} removed.")

            return Response({'status': 'success', 'message': 'Project and files created successfully.'}, status=status.HTTP_201_CREATED)

        except git.exc.GitError as e:
            logger.error(f"Git error during clone: {str(e)}")
            return Response({'status': 'error', 'message': f'Git error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            if repo_dir and os.path.exists(repo_dir):
                logger.info(f"Cleaning up directory due to error: {repo_dir}")
                shutil.rmtree(repo_dir)
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserProjectsView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            search_term = request.query_params.get('search', '')
            projects = Project.objects.filter(owner=user)
            if search_term:
                projects = projects.filter(name__icontains=search_term)

            serializer = ProjectSerializer(projects, many=True)
            return Response({'status': 'success', 'projects': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ListFilesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_name):
        try:
            user = request.user
            project = get_object_or_404(Project, name=project_name, owner=user)
            files = File.objects.filter(project=project)

            files_list = [{'file_path': file.file_path, 'extension': file.extension} for file in files]
            return Response({'status': 'success', 'files': files_list}, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FileContentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_name, file_path):
        try:
            user = request.user
            project = get_object_or_404(Project, name=project_name, owner=user)
            file = get_object_or_404(File, project=project, file_path=file_path)
            return Response({'status': 'success', 'content': file.content}, status=status.HTTP_200_OK)
        except (Project.DoesNotExist, File.DoesNotExist):
            return Response({'status': 'error', 'message': 'Project or file not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, project_name, file_path):
        try:
            user = request.user
            project = get_object_or_404(Project, name=project_name, owner=user)
            file = get_object_or_404(File, project=project, file_path=file_path)
            data = request.data
            new_content = data.get('content', '')
            file.content = new_content
            file.save(update_fields=['content'])
            return Response({'status': 'success', 'message': 'File updated successfully.'}, status=status.HTTP_200_OK)
        except (Project.DoesNotExist, File.DoesNotExist):
            return Response({'status': 'error', 'message': 'Project or file not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreateContainerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            data = request.data
            project_name = data.get('project_name')
            build_file_path = data.get('build_file_path', '')
            port = data.get('port', 8080)

            if not project_name:
                return Response({'status': 'error', 'message': 'Project name is required.'}, status=status.HTTP_400_BAD_REQUEST)

            project = Project.objects.get(name=project_name, owner=request.user)

            files = File.objects.filter(project=project)
            for file in files:
                file.to_host = True
                file.save()
                logger.info(f"File {file.file_path}: to_host set to {file.to_host}")

            build_file_path = project.build_file_path if build_file_path == '' else build_file_path
            if build_file_path.startswith('./'):
                build_file_path = build_file_path[2:]

            logger.info(f"Building image for project {project_name} using Dockerfile: {build_file_path}")

            client = docker.DockerClient(base_url=settings.DIND_URL)

            build_context_path = f"/app/repos/{project_name}"
            dockerfile_path = f"{build_context_path}/{build_file_path}"

            logger.info(f"Path to dockerfile: {dockerfile_path}")

            # Always rebuild the image without cache
            image, build_logs = client.images.build(
                path=build_context_path,
                dockerfile=dockerfile_path,
                tag=f"{project_name}_image",
                nocache=True
            )
            for log in build_logs:
                logger.info(log)

            container_name = f"{project_name}_container"

            container = client.containers.run(
                image=f"{project_name}_image",
                detach=True,
                ports={f"{port}/tcp": port},
                name=container_name
            )

            Container.objects.create(
                project=project,
                container_id=container.id,
                container_name=container_name,
                status='running',
                port=port,
            )

            return Response({
                'status': 'success',
                'container_id': container.id,
                'message': 'Container created and started successfully.'
            }, status=status.HTTP_201_CREATED)

        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)
        except docker.errors.DockerException as e:
            logger.error(f"Docker error: {str(e)}")
            return Response({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class ListContainersView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, project_name=None):
        try:
            user = request.user
            if project_name:
                project = get_object_or_404(Project, name=project_name, owner=user)
                containers = Container.objects.filter(project=project)
            else:
                containers = Container.objects.filter(project__owner=user)

            serializer = ContainerSerializer(containers, many=True)
            return Response({'status': 'success', 'containers': serializer.data}, status=status.HTTP_200_OK)

        except Project.DoesNotExist:
            return Response({'status': 'error', 'message': 'Project not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StartContainerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, container_id):
        try:
            container_db = Container.objects.get(container_id=container_id, project__owner=request.user)
            client = docker.DockerClient(base_url=settings.DIND_URL)
            container = client.containers.get(container_id)
            container.start()
            container.reload()
            # Update status from Docker container state
            docker_status = container.attrs['State']['Status']
            container_db.status = docker_status
            container_db.save()
            return Response({'status': 'success', 'message': f'Container {container_id} started successfully.', 'new_status': docker_status}, status=status.HTTP_200_OK)
        except Container.DoesNotExist:
            return Response({'status': 'error', 'message': 'Container not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)
        except docker.errors.DockerException as e:
            return Response({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StopContainerView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, container_id):
        try:
            container_db = Container.objects.get(container_id=container_id, project__owner=request.user)
            client = docker.DockerClient(base_url=settings.DIND_URL)
            container = client.containers.get(container_id)
            container.stop()
            container.reload()
            docker_status = container.attrs['State']['Status']
            container_db.status = docker_status
            container_db.save()
            return Response({'status': 'success', 'message': f'Container {container_id} stopped successfully.', 'new_status': docker_status}, status=status.HTTP_200_OK)
        except Container.DoesNotExist:
            return Response({'status': 'error', 'message': 'Container not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)
        except docker.errors.DockerException as e:
            return Response({'status': 'error', 'message': f'Docker error: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            return Response({'status': 'error', 'message': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SetToHostFlagView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, project_name, flag_value):
        try:
            project = Project.objects.get(name=project_name, owner=request.user)

            if flag_value.lower() == 'true':
                flag = True
            elif flag_value.lower() == 'false':
                flag = False
            else:
                return Response({'status': 'error', 'message': 'Invalid flag value. Use "true" or "false".'}, status=status.HTTP_400_BAD_REQUEST)

            File.objects.filter(project=project).update(to_host=flag)
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

class ContainerProxyView(APIView):
    authentication_classes = []
    permission_classes = []

    def dispatch(self, request, *args, **kwargs):
        self.container_name = kwargs.get("container_name")
        # Remove any leading slash to avoid "//" in the URL
        self.forwarded_path = kwargs.get("path", "").lstrip("/")
        return super().dispatch(request, *args, **kwargs)

    def _get_target_container(self):
        container = Container.objects.filter(container_name=self.container_name).first()
        if not container:
            logger.error(f"Container '{self.container_name}' not found.")
        return container

    def filter_headers(self, headers):
        # Remove headers that might cause issues
        excluded_headers = {"host", "content-length", "connection", "accept-encoding"}
        return {k: v for k, v in headers.items() if k.lower() not in excluded_headers}

    def proxy_request(self, request, target_url, headers):
        try:
            filtered_headers = self.filter_headers(headers)
            response = requests.request(
                method=request.method,
                url=target_url,
                headers=filtered_headers,
                data=request.body if request.body else None,
                allow_redirects=False,
                timeout=5,
                stream=True  # stream response content
            )
            return response
        except requests.RequestException as e:
            logger.error(f"Proxy request failed: {e}")
            return None

    def process_proxy(self, request):
        container = self._get_target_container()
        if not container:
            return Response({"error": "Container not found."}, status=404)

        # Build the target URL (ensure we don't accidentally include extra slashes)
        target_url = f"http://dind:{container.port}/{self.forwarded_path}"
        if request.META.get("QUERY_STRING"):
            target_url += f"?{request.META['QUERY_STRING']}"

        logger.info(f"Forwarding request to: {target_url}")
        proxied_response = self.proxy_request(request, target_url, request.headers)
        if proxied_response is None:
            return Response({"error": "Error forwarding request."}, status=500)

        # Build a streaming response using the proxied content
        response = StreamingHttpResponse(
            proxied_response.iter_content(chunk_size=8192),
            status=proxied_response.status_code,
            reason=proxied_response.reason,
        )

        # Copy headers from the proxied response, excluding a few that Django manages
        excluded_headers = {"content-encoding", "transfer-encoding", "connection", "keep-alive"}
        for header, value in proxied_response.headers.items():
            if header.lower() not in excluded_headers:
                response[header] = value

        return response

    def get(self, request, *args, **kwargs): 
        return self.process_proxy(request)

    def post(self, request, *args, **kwargs): 
        return self.process_proxy(request)

    def put(self, request, *args, **kwargs): 
        return self.process_proxy(request)

    def patch(self, request, *args, **kwargs): 
        return self.process_proxy(request)

    def delete(self, request, *args, **kwargs): 
        return self.process_proxy(request)

    def head(self, request, *args, **kwargs): 
        return self.process_proxy(request)

    def options(self, request, *args, **kwargs): 
        return self.process_proxy(request)