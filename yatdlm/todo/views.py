from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseNotFound
from django.shortcuts import render

from .models import TodoList
from .models import Task

# Create your views here.

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
    }
    return render(request, 'todo/index.html', context)

def list(request, list_id=-1, xhr=False):
    # Retrieve the list
    todo_list = TodoList.objects.get(id=list_id)
    # Retrieve the subsequent tasks
    tasks_filter = Task.objects.filter(parent_list=list_id)
    tasks = [task for task in tasks_filter]

    # Create the context
    context = {
        'list'  : todo_list,
        'tasks' : tasks,
        'xhr'   : xhr,
    }
    return render(request, 'todo/list.html', context)

def add_task(request, list_id=-1):
    title = request.POST['title']
    descr = request.POST['descr']

    new_task = Task(title=title, description=descr, parent_list_id=list_id)
    new_task.save()

    return list(request, list_id=list_id, xhr=True)

def del_task(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.delete()
    else: # If the task does not exists in DB, raises a 404
        raise HttpResponseNotFound("Task does not exists")
    return list(request, list_id=list_id, xhr=True)

def mark_as_done(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.is_done = not task.is_done
        task.save()
    else: # Raise a 404 if the task does not exists
        raise HttpResponseNotFound("Task does not exists")
    return list(request, list_id=list_id, xhr=True)