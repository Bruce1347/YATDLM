from functools import wraps
from todo.models import Task, NotOwner

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