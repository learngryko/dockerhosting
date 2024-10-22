import os
import git
import shutil  # for deleting the repo folder
import logging
import json
from django.conf import settings
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from .models import Project, File
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
    

