from django.contrib import admin
from .models import *

admin.site.register(Project)
admin.site.register(Environment)
admin.site.register(File)
admin.site.register(Container)
