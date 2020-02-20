from functools import wraps
from todo.models import Task, NotOwner
from django.http import JsonResponse

def task_exists(view):
    @wraps(view)
    def task_does_exists(request, list_id, task_id, *args, **kwargs):
        try:
            task = Task.objects.get(id=task_id, parent_list_id=list_id)
            request.task = task
            return view(request, list_id, task_id, *args, **kwargs)
        except Task.DoesNotExist:
            return JsonResponse({"errors": "The given task does not exists."}, status=404)
    return task_does_exists

def task_ownership(view):
    @wraps(view)
    def validate_ownership(*args, **kwargs):
        task = Task.objects.get(id=task_id, parent_list_id=list_id)
        if not task.is_owned(request.user):
            if not request.errors:
                request.errors = []
            request.errors.append(NotOwner)
        view(*args, **kwargs)
    return validate_ownership