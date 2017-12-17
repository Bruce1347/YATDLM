from django.db import models
from django.utils import timezone

class TodoList(models.Model):
    # A short description of the todo list (mandatory)
    title = models.CharField(max_length=100, blank=False)
    # The full description of the todo list 
    description = models.CharField(max_length=600, blank=True)
    # We want the creation date of the list (mandatory)
    creation_date = models.DateTimeField(auto_now_add=True)
    # The user may want the task completed upon a certain date
    due_date = models.DateTimeField(auto_now_add=False, default=timezone.now, blank=True)

class Task(models.Model):
    # The primary key to the list that contains this task
    parent_list = models.ForeignKey('TodoList', on_delete=models.CASCADE)
    # The primary key to the parent task, since a task can have subtasks, this is a recursive relationship
    parent_task = models.ForeignKey('self', on_delete=models.CASCADE)

    # A short description of the task (mandatory)
    title = models.CharField(max_length=100, blank=False)
    # Its full description
    description = models.CharField(max_length=300, blank=True)