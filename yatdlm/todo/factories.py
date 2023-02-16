from factory import LazyAttribute, SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from .models import Task, TodoList, User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("email")
    email = Faker("email")


class TodoListFactory(DjangoModelFactory):
    class Meta:
        model = TodoList

    owner = SubFactory(UserFactory)
    title = Faker("sentence")
    description = Faker("text")
    is_public = False


class TaskFactory(DjangoModelFactory):
    class Meta:
        model = Task

    parent_list = SubFactory(TodoListFactory)
    owner = LazyAttribute(lambda obj: obj.parent_list.owner)
    title = Faker("sentence")
    description = Faker("text")
    priority = Task.NORMAL
