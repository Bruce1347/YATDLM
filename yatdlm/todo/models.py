from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User

class TodoList(models.Model):
    # The owner of the todo list
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=1)

    # A short description of the todo list (mandatory)
    title = models.CharField(max_length=100, blank=False)
    
    # The full description of the todo list (optional)
    description = models.TextField(max_length=600, blank=True)

    # We want the creation date of the list (mandatory)
    creation_date = models.DateTimeField(auto_now_add=True)

    # The user may want the todo list completed upon a certain date (optional)
    due_date = models.DateTimeField(auto_now_add=False, default=timezone.now, blank=True, null=True)

    # Define if the list should be private or not (by default, yes)
    is_public = models.BooleanField(blank=False, null=False, default=False)

    # Identify the todolist with its title
    def __str__(self):
        return self.title

class TodoListAdmin(admin.ModelAdmin):
    readonly_fields=('creation_date',)

class Task(models.Model):
    # The user that created the task
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=1)

    # Priority levels
    priority_levels = ((1, "Urgent"),
                       (2, "Pressé"),
                       (3, "Normal"),
                       (4, "Y a le temps"),
                       (6, "A considérer"),
                       (7, "Résolu"))

    # Admin definitions
    fields = ['owner', 'parent_list', 'parent_task', 'creation_date', 'due_date',
              'resolution_date', 'title', 'description', 'is_done', 'priority']

    # The primary key to the list that contains this task
    parent_list = models.ForeignKey('TodoList', on_delete=models.CASCADE)

    # The primary key to the parent task, since a task can have subtasks, this is a recursive
    # relationship
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE,
                                    null=True, blank=True)

    # Creation date (mandatory, automatically created and inalterable)
    creation_date = models.DateTimeField(auto_now_add=True)

    # The user may want to complete the task within a certain time (optional)
    due_date = models.DateTimeField(auto_now=False, default=None, null=True, blank=True)

    resolution_date = models.DateTimeField(auto_now=False, default=None, null=True, blank=True)

    # A short description of the task (mandatory)
    title = models.CharField(max_length=300, blank=False)
    # Its full description (optional)
    description = models.TextField(max_length=700, blank=True)

    # Value that indicates if the task was completed or not
    is_done = models.BooleanField(blank=False, null=False, default=False)

    # Priority of the task
    priority = models.IntegerField(choices=priority_levels, default=3)

    # Identify the task with its title
    def __str__(self):
        return self.title


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_date',)

class FollowUp(models.Model):
    # Kinds of Follow-ups
    possible_follow_ups = ((1, "Commentaire"),
                           (2, "Modification"),
                           (3, "Changement d'État"))

    # The user that wrote the Follow-up
    writer = models.ForeignKey(User, on_delete=models.CASCADE, null=False, default=1)
 
    # Type of follow up (State change or comment)
    f_type = models.IntegerField(choices=possible_follow_ups, default=1)

    # We keep the changes if there is a priority state change
    old_priority = models.IntegerField(choices=Task.priority_levels, null=True, blank=True, default=None)
    new_priority = models.IntegerField(choices=Task.priority_levels, null=True, blank=True, default=None)

    # The task and list that the Follow-up refers to 
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=False)
    todol = models.ForeignKey('TodoList', on_delete=models.CASCADE, null=False)

    # Creation date (mandatory, automatically created and inalterable)
    creation_date = models.DateTimeField(auto_now_add=True)

    # The followup content, since it may refer to a specific problem that needs explanations, the max_length is longer than usual
    content = models.TextField(max_length=1000, blank=True)

    # Admin fields
    fields = ['task', 'todol']

class FollowUpAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_date',)