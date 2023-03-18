from http import HTTPStatus

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from todo.factories import TodoListFactory, UserFactory
from todo.models import TodoList


class TodoListCreate(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test",
            password=make_password(cls.users_password),
        )
        cls.url = "/todo/lists/add"

    def test_create_list(self):
        payload = {
            "title": "A todo list",
            "description": "A description for the said todo list.",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password),

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_list_empty_name(self):
        payload = {
            "title": "",
            "description": "A description for the said todo list",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

        # Todolist should not be created
        assert TodoList.objects.count() == 0

    def test_create_list_null_name(self):
        payload = {
            "description": "A description for the said todo list",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

        # Todolist should not be created
        assert TodoList.objects.count() == 0

    def test_create_list_null_description(self):
        payload = {
            "title": "Todolist",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # List should be created
        assert TodoList.objects.count() == 1
        todolist = TodoList.objects.first()

        assert todolist.title == "Todolist"
        assert todolist.description == ""
        assert todolist.is_public

    def test_create_list_no_visibility(self):
        payload = {
            "title": "Todolist",
        }

        self.client.login(username="test", password=self.users_password)

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # List should be created
        assert TodoList.objects.filter(
            title="Todolist", description="", is_public=False
        ).exists()


class TodoListDelete(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test", password=make_password(cls.users_password)
        )
        cls.other_user = UserFactory.create(
            username="test2", password=make_password(cls.users_password)
        )
        cls.list_ = TodoListFactory.create(owner=cls.user)
        cls.url = "/todo/lists/delete/{}"

    def test_delete_list(self):
        self.client.login(username="test", password=self.users_password)
        response = self.client.delete(self.url.format(self.list_.id))

        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)
        self.assertEqual(TodoList.objects.filter(id=self.list_.id).exists(), False)

    def test_delete_list_wrong_user(self):
        list_ = TodoList(owner=self.other_user)
        list_.save()

        self.client.login(username="test", password=self.users_password)
        response = self.client.delete(self.url.format(list_.id))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)
        self.assertEqual(TodoList.objects.filter(id=list_.id).exists(), True)

    def test_delete_list_user_not_logged(self):
        response = self.client.delete(self.url.format(self.list_.id))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_delete_list_wrong_verb(self):
        self.client.login(username="test", password="1234")
        self.client.login(username="test", password="1234")
        response = self.client.post(self.url.format(self.list_.id))

        # Expect a Method not allowed
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)
        self.assertEqual(TodoList.objects.filter(id=self.list_.id).exists(), True)
