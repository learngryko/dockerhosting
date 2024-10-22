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
from project.app.views import CloneRepositoryView, ListFilesView, FileContentView, CSRFTokenView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clone-repo/', CloneRepositoryView.as_view(), name='clone_repository'),
    path('projects/<str:project_name>/files/', ListFilesView.as_view(), name='list_files'),
    path('projects/<str:project_name>/files/<str:file_path>/', FileContentView.as_view(), name='file_content'),
    path('get-csrf-token/', CSRFTokenView.as_view(), name='get_csrf_token'),
]
