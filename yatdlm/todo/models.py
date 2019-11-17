from django.db import models
from django.utils import timezone
from django.contrib import admin
from django.contrib.auth.models import User
from django.utils.timezone import make_aware
from datetime import datetime

from django.utils.formats import date_format

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
    URGENT = 1
    NORMAL = 2
    TOCONSIDER = 3
    SOLVED = 4
    priority_levels = ((URGENT, "Urgent"),
                       (NORMAL, "Normal"),
                       (TOCONSIDER, "A considérer"),
                       (SOLVED, "Résolu"))

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

    # A task number
    task_no = models.IntegerField(default=0)

    # Identify the task with its title
    def __str__(self):
        return self.title

    def get_followups(self):
        followups = FollowUp.objects.filter(task=self.id)
        return followups

    def add_followup(self, followup, writer):
        followup = FollowUp(
            f_type=FollowUp.COMMENT,
            writer=writer,
            content=followup,
            todol=self.parent_list,
            task=self)
        followup.save()

    def change_state(self, comment=None, writer=None):
        """Changes the is_done state of the current Task instance.
        If ``comment`` is not None then the current task will have a
        newly added followup that will explain why the task was closed by
        a user (if they provided a comment).

        :param comment: The text followup written by the user when closing the
        task."""

        self.is_done = not self.is_done

        if self.is_done:
            new_priority = Task.SOLVED
        else:
            new_priority = Task.NORMAL
        followup = FollowUp(
            writer=writer,
            task=self,
            f_type=FollowUp.STATE_CHANGE,
            todol=self.parent_list,
            content=comment,
            old_priority=self.priority,
            new_priority=new_priority)
        followup.save()
        self.priority = new_priority
        
        if self.is_done:
            self.resolution_date = make_aware(datetime.now())
        else:
            self.resolution_date = None

    def as_dict(self, dates_format="d/m/Y"):
        """Returns a dict representation for the task"""
        resp = {
            'id' : self.id,
            'list_id': self.parent_list.id,
            'no': self.task_no,
            'title': self.title,
            'is_done': self.is_done,
            # Provide the user a shorter title for display
            'title_cropped': self.title[:40],
            'description': self.description,
            'creation_date': date_format(self.creation_date, dates_format),
            'creation_hour': date_format(self.creation_date, "H:i"),
            'priority': self.priority,
            'priority_str': self.get_priority_display()
        }

        if self.due_date is not None:
            resp['due_date'] = date_format(self.due_date, dates_format)
        
        if self.resolution_date is not None:
            resp['resolution_date'] = date_format(self.resolution_date, dates_format)
            resp['resolution_hour'] = date_format(self.resolution_date, "H:i")

        return resp


class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_date',)
    list_display= ('title', 'creation_date', 'priority', 'is_done',)

class FollowUp(models.Model):
    # Kinds of Follow-ups
    COMMENT = 1
    MODIFICATION = 2
    STATE_CHANGE = 3
    possible_follow_ups = ((COMMENT, "Commentaire"),
                           (MODIFICATION, "Modification"),
                           (STATE_CHANGE, "Changement d'État"))

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

    def as_dict(self):
        return {
            'writer': self.writer.username,
            'creation_date': date_format(self.creation_date, "d/m/Y à H:i"),
            'content': self.content,
            'old_priority': self.get_old_priority_display(),
            'new_priority': self.get_new_priority_display(),
            'type': self.f_type
        }

    # Admin fields
    fields = ['task', 'todol']

class FollowUpAdmin(admin.ModelAdmin):
    readonly_fields = ('creation_date',)