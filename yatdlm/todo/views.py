from datetime import datetime
from django.utils.timezone import make_aware
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import TodoList
from .models import Task

@login_required()
def index(request):
    # Fetch all the lists
    todo_lists = TodoList.objects.all()
    # Dictionary with all the existing tasks with their parent as key
    tasks = {}
    for todo in todo_lists:
        # Fetch the tasks that have `todo` as a parent
        children_tasks = Task.objects.filter(parent_list=todo.id)
        tasks[todo.id] = []
        for task in children_tasks:
            tasks[todo.id].append(task)

    context = {
        'lists' : todo_lists,
        'tasks' : tasks,
        'title_page' : 'Mes listes',
    }
    return render(request, 'todo/index.html', context)

@login_required()
def list(request, list_id=-1, xhr=False):
    # Retrieve the list
    todo_list = TodoList.objects.get(id=list_id)
    # Retrieve the subsequent tasks
    tasks_filter = Task.objects.filter(parent_list=list_id).order_by('is_done', 'creation_date')
    tasks = [task for task in tasks_filter]

    # Create the context
    context = {
        'list'  : todo_list,
        'tasks' : tasks,
        'xhr'   : xhr,
        'title_page' : todo_list.title,
        'priority_levels' : [level for level in Task.priority_levels]
    }
    return render(request, 'todo/list.html', context)

@login_required()
def add_task(request, list_id=-1):
    title = request.POST['title']
    descr = request.POST['descr']
    due = request.POST['due']
    prio = int(request.POST['priority'])

    new_task = Task(title=title, description=descr, priority=prio, parent_list_id=list_id)
    new_task.save()

    return list(request, list_id=list_id, xhr=True)

@login_required()
def del_task(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.delete()
    else: # If the task does not exists in DB, raises a 404
        raise HttpResponseNotFound("Task does not exists")
    return list(request, list_id=list_id, xhr=True)

@login_required()
def mark_as_done(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.is_done = not task.is_done
        if task.is_done:
            task.resolution_date = make_aware(datetime.now())
        task.save()
    else: # Raise a 404 if the task does not exists
        raise HttpResponseNotFound("Task does not exists")
    return list(request, list_id=list_id, xhr=True)