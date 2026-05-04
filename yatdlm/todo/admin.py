from django.contrib import admin

from .categories.models import Category, CategoryAdmin
from .models import (FollowUp, FollowUpAdmin, Task, TaskAdmin, TodoList,
                     TodoListAdmin)

# We register our models in order to be able to modify them in the admin interface
admin.site.register(Task, TaskAdmin)
admin.site.register(TodoList, TodoListAdmin)
admin.site.register(FollowUp, FollowUpAdmin)
admin.site.register(Category, CategoryAdmin)
