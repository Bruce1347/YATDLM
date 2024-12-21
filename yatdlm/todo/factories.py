from factory import LazyAttribute, SubFactory, post_generation
from factory.django import DjangoModelFactory
from factory.faker import Faker

from django.contrib.auth.hashers import make_password

from .models import Task, TodoList, User


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker("email")
    email = Faker("email")

    @post_generation
    def set_password(obj: User, create, extracted, **kwargs):
        if not create:
            # Object hasn't been persisted to db, skip
            return

        password = extracted or "1234"

        obj.password = make_password(password)
        obj.save()


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
