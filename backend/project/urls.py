"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from project.app.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('clone-repo/', CloneRepositoryView.as_view(), name='clone_repository'),
    path('projects/<str:project_name>/files/', ListFilesView.as_view(), name='list_files'),
    path('projects/<str:project_name>/files/<str:file_path>/', FileContentView.as_view(), name='file_content'),
    path('project/<str:project_name>/set-to-host/<str:flag_value>/', SetToHostFlagView.as_view(), name='set_to_host_flag'),
    path('create-container/', CreateContainerView.as_view(), name='create_container'),  # Create container
    path('containers/<str:project_name>/', ListContainersView.as_view(), name='list_containers'),  # List containers for a project
    path('containers/<str:container_id>/start/', StartContainerView.as_view(), name='start_container'),  # Start a container
    path('containers/<str:container_id>/stop/', StopContainerView.as_view(), name='stop_container'),  # Stop a container

]
