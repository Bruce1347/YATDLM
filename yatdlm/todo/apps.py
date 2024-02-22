from django.apps import AppConfig
from django.db.models.signals import pre_init, pre_save


class TodoConfig(AppConfig):
    name = "todo"

    def init_signals(self):
        from todo.signals import set_task_no
        from todo.models import Task

        pre_save.connect(set_task_no, sender=Task)

    def ready(self) -> None:
        # Once apps were loaded, init the signals
        self.init_signals()
