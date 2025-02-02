# urls.py

from django.contrib import admin
from django.urls import path
from project.app.views import *
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/logout/', LogoutView.as_view(), name='logout'),

    path('api/clone-repo/', CloneRepositoryView.as_view(), name='clone_repository'),
    path('api/user/projects/', UserProjectsView.as_view(), name='user_projects'),
    path('api/projects/<str:project_name>/files/', ListFilesView.as_view(), name='list_files'),
    path('api/projects/<str:project_name>/files/<path:file_path>/', FileContentView.as_view(), name='file_content'),
    path('api/project/<str:project_name>/set-to-host/<str:flag_value>/', SetToHostFlagView.as_view(), name='set_to_host_flag'),

    path('api/containers/', ListContainersView.as_view(), name='list_containers'),
    path('api/containers/create/', CreateContainerView.as_view(), name='create_container'),
    path('api/containers/<str:project_name>/', ListContainersView.as_view(), name='list_containers_project'),
    path('api/containers/<str:container_id>/start/', StartContainerView.as_view(), name='start_container'),
    path('api/containers/<str:container_id>/stop/', StopContainerView.as_view(), name='stop_container'),
    
    path('proxy/<str:container_name>/<path:path>', ContainerProxyView.as_view(), name='container-proxy'),
    path('proxy/<str:container_name>/', ContainerProxyView.as_view(), name='container-proxy-root'),
]
