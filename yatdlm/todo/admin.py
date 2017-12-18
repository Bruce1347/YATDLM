from django.contrib import admin

from .models import TodoList
from .models import Task

# We register our models in order to be able to modify them in the admin interface
admin.site.register(Task)
admin.site.register(TodoList)