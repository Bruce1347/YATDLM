from .models import Task


def set_task_no(sender, *, args=None, signal=None, instance=None, **kwargs):
    if instance and not instance.task_no:
        # Instance's task_no hasn't been persisted into db yet, count must be incremented by 1
        instance.task_no = (
            Task.objects.filter(parent_list_id=instance.parent_list_id).count() + 1
        )
