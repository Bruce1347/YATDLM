from django.contrib import admin

from .models import FollowUp
from .models import FollowUpAdmin
from .models import TodoListAdmin
from .models import TodoList
from .models import TaskAdmin
from .models import Task

# We register our models in order to be able to modify them in the admin interface
admin.site.register(Task, TaskAdmin)
admin.site.register(TodoList, TodoListAdmin)
admin.site.register(FollowUp, FollowUpAdmin)