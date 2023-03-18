from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

from todo.models import Task, TodoList


class Command(BaseCommand):
    help = "Populates the database with todolists and tasks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--nb_todolists",
            nargs=1,
            type=int,
            default=1,
            help="The number of created todolists (default value : 1)",
        )
        parser.add_argument(
            "--todolist_name",
            nargs="+",
            type=str,
            help="The name(s) of the newly created todolist(s)",
        )
        parser.add_argument("nb_tasks", nargs=1, type=int)
        parser.add_argument("nb_subtasks", nargs=1, type=int)
        parser.add_argument("--owner", nargs=1, type=str, default="bruce")

    def handle(self, *args, **kwargs):
        # Manual unpacking here since the integer values will be
        # encapsulated inside a list
        nb_todolists = kwargs["nb_todolists"][0]
        nb_subtasks = kwargs["nb_subtasks"][0]
        nb_tasks = kwargs["nb_tasks"][0]
        owner = kwargs["owner"]
        todolist_names = kwargs["todolist_name"]

        if todolist_names is not None and nb_todolists != len(todolist_names):
            error_msg = (
                "Length of todolists names and number of todolists mismatch: %d != %d"
            )
            raise CommandError(error_msg % (len(todolist_names), nb_todolists))

        print(owner)
        owner = User.objects.get(username=owner)

        lists = [TodoList(owner=owner) for i in range(nb_todolists)]
        if todolist_names:
            for name, todolist in zip(todolist_names, lists):
                todolist.title = name
        # Insert all the lists with only one query
        TodoList.objects.bulk_create(lists)
        # Retrieve all the saved lists, this is a mandatory step since django's
        # bulk_create will NOT populate the model's primary key after insertion.
        lists = TodoList.objects
        if todolist_names:
            lists = lists.filter(title__in=todolist_names)

        tasks = []
        subtasks = []

        # First step: Create the tasks
        for todolist in lists.all():
            for i in range(nb_tasks):
                task = Task(owner=owner, parent_list=todolist, title=str(i))
                tasks.append(task)

        # Bulk insert the tasks
        Task.objects.bulk_create(tasks)
        # Retrieve the newly created task (see the why in line 49)
        tasks = Task.objects.filter(owner=owner)
        # Then bulk insert the subtasks, we cannot create the tasks and their
        # subtasks in the same SQL query since the subtasks will refer to their
        # parents that will no exist in the database at the time of insertion
        for task in tasks:
            for i in range(nb_subtasks):
                task = Task(
                    owner=owner, parent_list=todolist, title=str(i), parent_task=task
                )
                subtasks.append(task)
        Task.objects.bulk_create(subtasks)
