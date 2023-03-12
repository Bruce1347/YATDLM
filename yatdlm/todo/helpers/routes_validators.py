from functools import wraps
from todo.models import Task, NotOwner
from django.http import JsonResponse


def task_exists(view):
    @wraps(view)
    def task_does_exists(request, list_id, task_id, *args, **kwargs):
        if Task.objects.filter(id=task_id, parent_list_id=list_id).exists():
            return view(request, list_id, task_id, *args, **kwargs)
        else:
            return JsonResponse(
                {"errors": "The given task does not exists."}, status=404
            )

    return task_does_exists


def task_ownership(view):
    @wraps(view)
    def validate_task_ownership(request, list_id, task_id, *args, **kwargs):
        if Task.objects.filter(
            id=task_id, parent_list_id=list_id, owner=request.user
        ).exists():
            return view(request, list_id, task_id, *args, **kwargs)
        else:
            return JsonResponse(
                {"errors": "The given task is not owned by the user."}, status=403
            )

    return validate_task_ownership
