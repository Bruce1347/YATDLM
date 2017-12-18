from django.shortcuts import render
from django.http import HttpResponse
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
        children_tasks = Task.objects.filter(id=todo.id)
        tasks[todo.id] = []
        for task in children_tasks:
            tasks[todo.id].append(task)

    print(tasks)

    context = {
        'lists' : todo_lists,
        'tasks' : tasks,
    }
    return render(request, 'todo/index.html', context)