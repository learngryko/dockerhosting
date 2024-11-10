from django.contrib import admin
from django.urls import path
from project.app.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),


    path('api/get-csrf-token/', get_csrf_token, name='get_csrf_token'),
    path('api/clone-repo/', CloneRepositoryView.as_view(), name='clone_repository'),
    path('api/projects/<str:project_name>/files/', ListFilesView.as_view(), name='list_files'),
    path('api/projects/<str:project_name>/files/<str:file_path>/', FileContentView.as_view(), name='file_content'),
    path('api/project/<str:project_name>/set-to-host/<str:flag_value>/', SetToHostFlagView.as_view(), name='set_to_host_flag'),
    path('api/create-container/', CreateContainerView.as_view(), name='create_container'),  # Create container
    path('api/containers/<str:project_name>/', ListContainersView.as_view(), name='list_containers'),  # List containers for a project
    path('api/containers/<str:container_id>/start/', StartContainerView.as_view(), name='start_container'),  # Start a container
    path('api/containers/<str:container_id>/stop/', StopContainerView.as_view(), name='stop_container'),  # Stop a container

]
