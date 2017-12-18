from django.db import models
from django.utils import timezone

class TodoList(models.Model):
    # A short description of the todo list (mandatory)
    title = models.CharField(max_length=100, blank=False)
    # The full description of the todo list (optional)
    description = models.TextField(max_length=600, blank=True)
    # We want the creation date of the list (mandatory)
    creation_date = models.DateTimeField(auto_now_add=True)
    # The user may want the todo list completed upon a certain date (optional)
    due_date = models.DateTimeField(auto_now_add=False, default=timezone.now, blank=True, null=True)

    # Identify the todolist with its title
    def __str__(self):
        return self.title

class Task(models.Model):
    # The primary key to the list that contains this task
    parent_list = models.ForeignKey('TodoList', on_delete=models.CASCADE)
    # The primary key to the parent task, since a task can have subtasks, this is a recursive relationship
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    # Creation date (mandatory, automatically created and inalterable)    
    creation_date = models.DateTimeField(auto_now_add=True)

    # The user may want to complete the task within a certain time (optional)
    due_date = models.DateTimeField(auto_now=False, default=timezone.now, null=True, blank=True)

    # A short description of the task (mandatory)
    title = models.CharField(max_length=100, blank=False)
    # Its full description (optional)
    description = models.TextField(max_length=300, blank=True)

    # Identify the task with its title
    def __str__(self):
        return self.title