import json
from datetime import datetime

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound, JsonResponse)
from django.shortcuts import redirect, render
from django.utils.timezone import make_aware
from django.views.decorators.http import require_http_methods

from .models import FollowUp, Task, TodoList
from .utils import yesnojs


@login_required()
def index(request, xhr):
    # Fetch all the lists
    todo_lists = TodoList.objects.filter(owner=request.user)

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
        'isdev' : 'DEV - ' if settings.DEBUG else '',
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

    tfilter = Task.objects.filter(parent_list_id=todo_list.id)
    # Retrieve the subsequent tasks
    tasks_filter = tfilter.order_by('is_done', 'priority', '-creation_date')

    # Create the context
    creation_years_filter = tfilter.dates('creation_date', 'year')
    deadlines_years_filter = tfilter.dates('due_date', 'year')
    resolution_years_filter = tfilter.dates('resolution_date', 'year')
    creation_years = [date.year for date in creation_years_filter]
    resolution_years = [date.year for date in resolution_years_filter]
    deadlines_years = [date.year for date in deadlines_years_filter]

    months = (
        ('Jan', 1),
        ('Fev', 2),
        ('Mar', 3),
        ('Avr', 4),
        ('Mai', 5),
        ('Juin', 6),
        ('Juil', 7),
        ('Août', 8),
        ('Sept', 9),
        ('Oct', 10),
        ('Nov', 11),
        ('Dec', 12)
    )

    context = {
        'list'  : todo_list,
        'tasks' : [task for task in tasks_filter],
        'followups': {
            task.task_no: task.get_followups()
            for task in tasks_filter},
        'xhr'   : xhr,
        'isdev' : 'DEV - ' if settings.DEBUG else '',
        'title_page' : todo_list.title,
        'priority_levels' : [level for level in Task.priority_levels],
        'public': public,
        'publicjs' : yesnojs(public),
        'creation_years': creation_years,
        'resolution_years': resolution_years,
        'deadlines_years': deadlines_years,
        'months': months
    }

    return render(request, 'todo/list.html', context)

@require_http_methods(['GET'])
def list_tasks(request, list_id=None):
    try:
        tasks = Task.objects.filter(parent_list_id=list_id).order_by('task_no')
        todo = TodoList.objects.get(id=list_id)
        if not todo.is_public:
            return JsonResponse({'errors': 'Non.'}, status=403)
        priorities = {
            name: value
            for name, value in Task.priority_levels
        }
        resp = {
            'tasks': [
                task.as_dict(dates_format="Y/m/d")
                for task in tasks],
            'priorities': priorities}
        resp_code = 200
    except Task.DoesNotExist:
        resp = {'errors': 'Invalid list ID'}
        resp_code = 404
    return JsonResponse(resp, status=resp_code)

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

    new_task = Task(
        owner=user,
        title=title,
        description=descr,
        priority=prio,
        parent_list_id=list_id,
        due_date=due,
        task_no=task_no)
    new_task.save()

    return display_list(request, list_id=list_id, xhr=True)

@login_required()
def add_task_experimental(request, list_id=None):
    """Adds a task to the database for the given list"""
    responsecode = 200
    json_body = dict()
    # Ensure that the body is decoded as plain text
    body = json.loads(request.body.decode("utf-8"))
    try:
        todo = TodoList.objects.get(id=list_id)
        if Task.objects.count() > 0:
            latest_task_no = Task.objects.values_list(
                'task_no',
                flat=True).latest('creation_date')
            task_no = latest_task_no + 1
        else:
            task_no = 1
        # TODO: Leverage the kwargs
        task = Task(
            parent_list=todo,
            title=body['title'],
            description=body['descr'],
            priority=int(body['priority']),
            due_date=datetime.strptime(body['due'], "%Y-%m-%d") if body['due'] != '' else None,
            owner=request.user,
            task_no=task_no
        )
        task.save()
        json_body = task.as_dict()
        json_body['creator'] = task.owner.username
    except TodoList.DoesNotExist:
        responsecode = 404
        json_body['errors'] = 'The given list does not exists'
    return JsonResponse(json_body, status=responsecode)

@login_required()
@require_http_methods(['PATCH'])
def update_task(request, list_id=None, task_id=None):
    if not list_id or not task_id:
        resp = {'errors': 'No ID given for a task or a list'}
        resp_code = 500
    else:
        try:
            task = Task.objects.get(id=task_id, parent_list_id=list_id)
            body = json.loads(request.body.decode("utf-8"))
            task.title = body.get('title')
            task.description = body.get('description')
            task.priority = int(body.get('priority'))
            task.save()
            resp = task.as_dict()
            resp_code = 202
        except TodoList.DoesNotExist:
            resp = {'errors': 'Wrong task ID or list ID'}
            resp_code = 404
    return JsonResponse(resp, status=resp_code)

@login_required()
@require_http_methods(['DELETE'])
def delete_task(request, list_id=None, task_id=None):
    """Deletes a task from the database"""
    if task_id is None or list_id is None:
        resp = {'errors': 'No ID given for a Task or a List'}
        resp_code = 404
    else:
        try:
            task = Task.objects.get(id=task_id, parent_list_id=list_id)
            task.delete()
            resp = {'status': 'OK'}
            resp_code = 200
        except Task.DoesNotExist:
            resp = {'errors': 'One of the given IDs is invalid'}
            resp_code = 404
    return JsonResponse(resp, status=resp_code)

@login_required()
@require_http_methods(['PATCH'])
def close_task(request, list_id=None, task_id=None):
    if not list_id or not task_id:
        status = 404
        payload = {"errors": "Task ID or List ID missing"}
    try:
        task = Task.objects.get(id=task_id, parent_list=list_id)
        body = json.loads(request.body.decode('utf-8'))
        if 'followup' in body:
            comment = body.get('followup')
        else:
            comment = ''
        task.change_state(comment=comment, writer=request.user)
        task.save()
        status = 202
        payload = task.as_dict()
    except Task.DoesNotExist:
        status = 404
        payload = {"errors": "Wrong Task ID or List ID"}
    return JsonResponse(payload, status=status)

@login_required()
@require_http_methods(['GET'])
def get_followups(request, list_id=None, task_id=None):
    if not list_id or not task_id:
        status = 500
        payload = {"errors": "No Task ID or List ID"}
    try:
        task = Task.objects.get(id=task_id, parent_list=list_id)
    except Task.DoesNotExist:
        status = 4040
        payload = {"errors": "Wrong Task ID or List ID"}
    return JsonResponse(payload, status=status)

@login_required()
def mark_as_done(request, list_id=-1, task_id=-1):
    if task_id != -1:
        task = Task.objects.get(id=task_id)
        task.is_done = not task.is_done

        if 'followup' in request.POST:
            followup = FollowUp(
                writer=request.user,
                task=task,
                f_type=FollowUp.STATE_CHANGE,
                todol_id=list_id,
                content=request.POST['followup'],
                old_priority=task.priority,
                new_priority=Task.SOLVED)
            followup.save()

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
        priority_levels = {level[0] : level[1] for level in Task.priority_levels}

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
        followup = FollowUp(
            writer=request.user,
            task_id=task_id,
            todol_id=list_id,
            content=request.POST['followup'])
        followup.save()
        return display_detail(
            request,
            list_id=list_id,
            task_id=task_id,
            add_followup=True,
            xhr=True)
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

    new_list = TodoList(
        owner=request.user,
        title=list_title,
        description=list_description,
        is_public=list_visibility)
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
