from django.contrib.auth.hashers import make_password
from factory import LazyAttribute, SubFactory, post_generation
from factory.django import DjangoModelFactory
from factory.faker import Faker

from .models import Task, TodoList, User


def debug(x):
    breakpoint()


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    class Params:
        plain_password: str | None = None

    username = Faker("email")
    email = Faker("email")
    password = LazyAttribute(
        lambda obj: make_password(obj.plain_password)
        if obj.plain_password
        else make_password("1234")
    )


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
