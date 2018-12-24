from datetime import datetime

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound)
from django.shortcuts import redirect, render
from django.utils.timezone import make_aware
from django.views.generic import TemplateView

from .models import FollowUp, Task, TodoList

from .utils import yesnojs

@login_required()
def index(request, xhr):
    # Fetch all the lists
    todo_lists = TodoList.objects.all()
    
    # Dict that contains the needed information for each list.
    # The key is the name of the list and the data corresponds to the needed infos
    table_context = {}

    for todo in todo_lists:
        opened_tasks = len(Task.objects.filter(parent_list=todo, is_done=False))
        done_tasks = len(Task.objects.filter(parent_list=todo, is_done=True))
        total_tasks = done_tasks + opened_tasks

        completion = done_tasks / (total_tasks) * 100.0 if total_tasks is not 0 else 0
        completion = round(completion, 2)

        table_context[todo.title] = {
            'title' : todo.title,
            'id' : todo.id,
            'opened_tasks' : opened_tasks,
            'completion' : completion,
            'creation_date' : todo.creation_date
        }

    context = {
        'lists' : [todo.title for todo in todo_lists],
        'page_title' : 'Mes listes',
        'context' : table_context,
        'xhr' : xhr
    }

    return render(request, 'todo/index.html', context)

def display_list(request, list_id=-1, xhr=False, public=False):
    # Retrieve the list
    todo_list = TodoList.objects.get(id=list_id)

    # If the list is not public then we throw a 403
    if not todo_list.is_public and public:
        return HttpResponseForbidden()

    # Retrieve the subsequent tasks
    tasks_filter = Task.objects.filter(parent_list=list_id).order_by('is_done', 'priority', '-creation_date')
    tasks = [task for task in tasks_filter]

    # Create the context
    context = {
        'list'  : todo_list,
        'tasks' : tasks,
        'xhr'   : xhr,
        'title_page' : todo_list.title,
        'priority_levels' : [level for level in Task.priority_levels],
        'public': public,
        'publicjs' : yesnojs(public)
    }

    return render(request, 'todo/list.html', context)

@login_required()
def add_task(request, list_id=-1):
    title = request.POST['title']
    descr = request.POST['descr']
    due = request.POST['due'] if request.POST['due'] is not "" else None
    user = request.user
    prio = int(request.POST['priority'])
    if Task.objects.count() > 0:
        latest_task_no = Task.objects.values_list(
            'task_no',
            flat=True).latest('creation_date')
        task_no = latest_task_no + 1
    else:
        task_no = 1

    new_task = Task(owner=user, title=title, description=descr, priority=prio, parent_list_id=list_id, due_date=due, task_no=task_no)
    new_task.save()

    return display_list(request, list_id=list_id, xhr=True)

@login_required()
def del_task(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.delete()
    else: # If the task does not exists in DB, raises a 404
        raise HttpResponseNotFound("Task does not exists")
    return display_list(request, list_id=list_id, xhr=True)

@login_required()
def mark_as_done(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.is_done = not task.is_done

        if 'followup' in request.POST:
            f = FollowUp(writer=request.user, task=task, 
                         f_type=FollowUp.STATE_CHANGE, todol_id=list_id,
                         content=request.POST['followup'],
                         old_priority=task.priority, new_priority=Task.SOLVED)
            f.save()

        if task.is_done:
            task.resolution_date = make_aware(datetime.now())
            task.priority = Task.SOLVED # Mark the task as solved

        task.save()
    else: # Raise a 404 if the task does not exists
        raise HttpResponseNotFound("Task does not exists")
    return display_list(request, list_id=list_id, xhr=True)

def display_detail(request, list_id=-1, task_id=-1, add_followup=False, xhr=False):
    if task_id != -1 and list_id != -1:
        public = 'public' in request.POST and request.POST['public'] == 'true'
        xhr = 'xhr' in request.POST and request.POST['xhr'] == 'true'
        task = Task.objects.get(id=task_id, parent_list_id=list_id)
        priority_levels = { level[0] : level[1] for level in Task.priority_levels }
        
        followups = FollowUp.objects.filter(task=task, todol_id=list_id).order_by('creation_date')

        return render(request, 'todo/xhr/task_detail.html', {
            'task': task,
            'followups' : followups,
            'xhr' : xhr,
            'public' : public,
            'list' : task.parent_list,
            'priority_levels' : priority_levels,
            'add_followup': add_followup
        })
    else:
        return HttpResponseNotFound("Task not found")

@login_required()
def add_followup(request, list_id=-1, task_id=-1):
    if task_id != -1 and list_id != -1:
        followup = FollowUp(writer=request.user, task_id=task_id, todol_id=list_id, content=request.POST['followup'])
        followup.save()
        return display_detail(request, list_id=list_id, task_id=task_id, add_followup=True, xhr=True)
    else:
        return HttpResponseNotFound("NOPE.")

@login_required()
def get_task_detail(request, list_id=-1, task_id=-1):
    if list_id != -1 and task_id != -1:
        task = Task.objects.get(id=task_id, parent_list_id=list_id)
        parent_list = task.parent_list

        context = {
            'task' : task,
            'list' : parent_list,
            'priority_levels' : Task.priority_levels
        }

        return render(request, 'todo/xhr/task_edit.html', context)
    else:
        return HttpResponseNotFound("NOPE.")

@login_required()
def task_update(request, list_id=-1, task_id=-1):
    if list_id != -1 and task_id != -1:
        task = Task.objects.get(id=task_id, parent_list_id=list_id)

        new_title = request.POST['title']
        new_description = request.POST['descr']
        new_priority = int(request.POST['prio'])

        new_state = FollowUp(writer=request.user, f_type=2,
                             task=task, todol_id=list_id,
                             old_priority=task.priority,
                             new_priority=new_priority)

        task.title = new_title
        task.description = new_description
        task.priority = new_priority

        task.save()
        new_state.save()

        return display_detail(request, list_id=list_id, task_id=task_id, xhr=True)
    else:
        return HttpResponseNotFound("NOPE.")

@login_required
def add_list(request):
    list_title = request.POST['title']
    list_description = request.POST['description']
    # list_deadline = request.POST['end_date']
    list_visibility = 'visibility' in request.POST and request.POST['visibility'] == "True"

    new_list = TodoList(owner=request.user, title=list_title, description=list_description, is_public=list_visibility)
    new_list.save()

    return index(request, True)

def display_login(request):
    if request.user and request.user.is_authenticated:
        return redirect('/todo')
    
    return render(request, 'todo/login.html')

def user_login(request):
    logout(request)

    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/todo')

    return HttpResponseNotFound()

def delete_list(request, list_id):
    try:
        xhr = request.POST['xhr'] == 'True'
        del_list = TodoList.objects.get(id=list_id)
        del_list.delete()
        if not xhr:
            return HttpResponse()
        else:
            return index(request, xhr=True)
    except ObjectDoesNotExist:
        return HttpResponseForbidden()
