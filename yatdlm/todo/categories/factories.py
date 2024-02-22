from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.faker import Faker

from todo.categories.models import Category
from todo.factories import TodoListFactory


class CategoryFactory(DjangoModelFactory):
    class Meta:
        model = Category

    todolist = SubFactory(TodoListFactory)

    name = Faker("word")
