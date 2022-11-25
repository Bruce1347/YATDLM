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

from .helpers.routes_validators import task_exists, task_ownership
from .models import FollowUp, NotOwner, Task, TodoList
from .utils import yesnojs, yesnopython

from django.contrib.auth.models import User

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
        'xhr' : xhr,
        'includes': ['lists_index']
    }

    return render(request, 'todo/index.html', context)

def display_list(request, list_id=-1, xhr=False, public=False):
    # Retrieve the list
    todo_list = TodoList.objects.select_related('owner').get(id=list_id)

    # If the list is not public then we throw a 403
    if not todo_list.is_public and public:
        return HttpResponseForbidden()

    # Retrieve the subsequent tasks
    tfilter = (
        Task.objects.filter(parent_list_id=todo_list.id)
        .select_related("owner", "parent_task")
        .prefetch_related("task_set", "categories")
        .order_by("is_done", "priority", "-resolution_date", "-creation_date")
        .all()
    )

    all_tasks = [task for task in tfilter]

    # Create the context
    creation_years = set(sorted([task.creation_date.year for task in all_tasks]))
    resolution_years = set(sorted([task.resolution_date.year for task in all_tasks if task.resolution_date]))
    deadlines_years = set(sorted([task.due_date.year for task in all_tasks if task.due_date]))

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
    subtasks = [task for task in all_tasks if task.parent_task is not None]
    tasks = [task for task in all_tasks if task.parent_task is None]

    tasks = {
        task.id: task
        for task in tasks
    }

    for task in subtasks:
        parent_task = tasks[task.parent_task.id]
        if not hasattr(parent_task, 'subtasks_render'):
            setattr(parent_task, 'subtasks_render', list())
        parent_task.subtasks_render.append(task)

    tasks = [task for _, task in tasks.items()]

    for task in tasks:
        setattr(task, 'str_owner', task.owner.username)
        str_categories = ", ".join((
            category.name
            for category in task.categories.all()
        ))
        setattr(task, 'str_categories', str_categories)

    context = {
        'list'  : todo_list,
        'list_owner': todo_list.owner.username,
        'tasks' : tasks,
        'xhr'   : xhr,
        'isdev' : 'DEV - ' if settings.DEBUG else '',
        'title_page' : todo_list.title,
        'priority_levels' : [level for level in Task.priority_levels],
        'public': public,
        'publicjs' : yesnojs(public),
        'creation_years': creation_years,
        'resolution_years': resolution_years,
        'deadlines_years': deadlines_years,
        'months': months,
        'includes': ['list', 'list_common']
    }

    return render(request, 'todo/list.html', context)

@require_http_methods(['GET'])
def list_tasks(request, list_id=None):
    try:
        #TODO: Use a validator for this verification
        todo = TodoList.objects.prefetch_related('task_set', 'category_set').get(id=list_id)
        if not todo.is_public and not request.user.is_authenticated:
            return JsonResponse({'errors': 'Non.'}, status=403)
        tasks = todo.task_set
        # Prefetch related objects
        tasks = tasks.select_related(
            'parent_task',
            'parent_list',
        )
        tasks = tasks.prefetch_related(
            'task_set',
            'task_set__task_set',
            'task_set__categories',
            'categories',   
        )
        # Order by task number
        tasks = tasks.order_by('task_no')
        # Execute the query
        tasks = [task for task in tasks]
        # Check if the user requests all the tasks or only the meta tasks
        # (without any parent task)
        meta_tasks_param = yesnopython(request.GET.get('meta_tasks', 'false'))
        if meta_tasks_param:
            tasks = [task for task in tasks if task.parent_task is None]
        priorities = {
            name: value
            for name, value in Task.priority_levels
        }
        categories = [
            cat.as_dict()
            for cat in todo.category_set.all()
        ]
        categories_str = [
            cat.name
            for cat in todo.category_set.all()
        ]
        resp = {
            'tasks': [],
            'priorities': priorities,
        }
        subtasks = {}
        for sub in Task.objects.prefetch_related('parent_task').filter(parent_task_id__in=[task.id for task in tasks]):
            if sub.parent_task_id not in subtasks:
                subtasks[sub.parent_task_id] = []
            subtasks[sub.parent_task_id].append(sub.as_dict())

        for task in tasks:
            task_dict = task.as_dict(dates_format="Y/m/d")
            task_dict['categories'] = categories
            task_dict['categories_str'] = categories_str
            if task.id in subtasks:
                task_dict['subtasks'] = subtasks[task.id]
                subtasks_done = [
                    1
                    for sub in subtasks[task.id]
                    if sub['is_done']
                ]
                task_dict['subtasks_progress'] = 100.0 * sum(subtasks_done) / len(subtasks[task.id])
            else:
                task_dict['subtasks'] = None
                task_dict['subtasks_progress'] = None
            resp['tasks'].append(task_dict)
        resp_code = 200
    except Task.DoesNotExist:
        resp = {'errors': 'Invalid list ID'}
        resp_code = 404
    return JsonResponse(resp, status=resp_code)

@login_required()
def add_task(request, list_id=None):
    """Adds a task to the database for the given list"""
    responsecode = 200
    json_body = dict()
    # Ensure that the body is decoded as plain text
    body = json.loads(request.body.decode("utf-8"))
    try:
        todo = TodoList.objects.get(id=list_id)
        task_no = todo.task_set.count() + 1
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
        if 'parent_task' in body:
            task.parent_task_id = int(body['parent_task'])
        task.save()
        if 'categories' in body:
            for category in body['categories']:
                task.categories.add(int(category))
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
            if request.user != task.owner:
                raise Task.IsNotOwner()
            body = json.loads(request.body.decode("utf-8"))
            new_priority = int(body.get('priority'))
            new_state = FollowUp(
                writer=request.user, 
                task=task, 
                todol_id=list_id,
                old_priority=task.priority,
                new_priority=new_priority)
            if new_priority is not task.priority:
                new_state.f_type = FollowUp.STATE_CHANGE
                task.priority = new_priority
            else:
                new_state.f_type = FollowUp.MODIFICATION
            new_state.save()
            task.title = body.get('title')
            task.description = body.get('description')
            if 'categories' in body:
                categories = [int(category) for category in body.get('categories')]
                task.categories.clear()
                # Add tasks in bulk through args unpacking
                task.categories.add(*categories)
            task.save()
            resp = task.as_dict()
            resp_code = 202
        except TodoList.DoesNotExist:
            resp = {'errors': 'Wrong task ID or list ID'}
            resp_code = 404
        except Task.IsNotOwner:
            resp = {'errors': 'Unauthorized'}
            resp_code = 403
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
        task = Task.objects.get(id=task_id, parent_list_id=list_id)
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

@require_http_methods(['GET'])
def get_followups(request, list_id=None, task_id=None):
    if not list_id or not task_id:
        status = 500
        payload = {"errors": "No Task ID or List ID"}
    try:
        task = Task.objects.get(id=task_id, parent_list=list_id)
        status = 200
        payload = {"followups": [f.as_dict() for f in task.get_followups()]}
    except Task.DoesNotExist:
        status = 404
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
@require_http_methods(['POST'])
def add_followup(request, list_id=None, task_id=None):
    try:
        task = Task.objects.get(id=task_id, parent_list=list_id)
        body = json.loads(request.body.decode('utf-8'))
        followup = body.get('followup')
        task.add_followup(followup, request.user)
        status = 200
        payload = {"status": "OK!"}
    except Task.DoesNotExist:
        status = 404
        payload = {"errors": "Wrong Task ID or List ID"}
    return JsonResponse(payload, status=status)

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

@login_required()
@require_http_methods(['DELETE'])
def delete_list(request, list_id):
    try:
        del_list = TodoList.objects.get(id=list_id)
        if del_list.owner != request.user:
            raise NotOwner
        del_list.delete()
        status_code = 204
        payload = {}
    except ObjectDoesNotExist:
        status_code = 404
        payload = {"errors": "Given list does not exists"}
    except NotOwner:
        status_code = 403
        payload = {"errors": "The logged user is not the owner of the List"}
    return JsonResponse(payload, status=status_code)


@login_required()
@require_http_methods(['PATCH'])
@task_exists
@task_ownership
def reject_task(request, list_id, task_id):
    task = request.task
    followup = ''
    raw_body = request.body.decode("utf-8")
    if raw_body:
        body = json.loads(raw_body)
        if 'followup' in body:
            followup = body['followup']
    task.reject(request.user, followup)
    return JsonResponse(task.as_dict(), status=202)


@require_http_methods(['GET'])
@login_required
@task_exists
@task_ownership
def display_task(request, list_id, task_id):
    if 'json' in request.GET:
        return JsonResponse(request.task.as_dict(), status=202)
    context = {
        'task': request.task,
        'public': False,
        'publicjs': yesnojs(False),
        'includes': ['single_task', 'list_common'],
        'followups': request.task.get_followups()
    }
    return render(request, 'todo/task.html', context)

@require_http_methods(['GET'])
@task_exists
def display_task_public(request, list_id, task_id):
    """Public version of ``display_task``, this is a duplicate function because
    of the usage of login dependant decorators in the previous function. This
    function ensures that the displayed task is displayed in a read-only mode.
    """
    if 'json' in request.GET:
        return JsonResponse(request.task.as_dict(), status=202)
    context = {
        'task': request.task,
        'public': True,
        'publicjs': yesnojs(True),
        'includes': ['single_task', 'list_common'],
        'followups': request.task.get_followups()
    }
    return render(request, 'todo/task.html', context)