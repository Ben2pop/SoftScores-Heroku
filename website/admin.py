from django.contrib import admin
from .models import Team, Project, DemoProject

# Register your models here.
admin.site.register(Team)
admin.site.register(Project)
admin.site.register(DemoProject)
