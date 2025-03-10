from http import HTTPStatus
from typing import Any, NamedTuple

from django.contrib.auth.hashers import make_password
from django.test import TestCase

from todo.factories import TodoListFactory, UserFactory
from todo.models import TodoList


# XXX: Remove once test parametrization is not needed anymore
class TestCaseConfig(NamedTuple):
    url: str
    status_code: HTTPStatus
    # Default to Django's default content type for cases where we don't need
    # to overload the content type.
    content_type: str | None = None


class TodoListCreate(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test",
            password=make_password(cls.users_password),
        )
        cls.url = "/todo/lists/add"

    urls_and_expected_status: dict[str, TestCaseConfig] = {
        "deprecated": TestCaseConfig("/todo/lists/add", HTTPStatus.OK),
        "current": TestCaseConfig(
            "/todo/beta/lists", HTTPStatus.CREATED, "application/json"
        ),
    }

    def _assert_create_list(self, version: str) -> None:
        payload = {
            "title": "A todo list",
            "description": "A description for the said todo list.",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        url, status_code, content_type = self.urls_and_expected_status[version]

        post_kwargs = {"data": payload}
        if content_type:
            post_kwargs["content_type"] = content_type

        response = self.client.post(url, **post_kwargs)

        self.assertEqual(response.status_code, status_code)

    def test_create_list(self):
        self._assert_create_list("current")

    def test_create_list_deprecated(self):
        self._assert_create_list("deprecated")

    def _assert_create_list_empty_name(self, version: str) -> None:
        payload = {
            "title": "",
            "description": "A description for the said todo list",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        url, _, content_type = self.urls_and_expected_status[version]

        post_kwargs: dict[str, dict[str | Any] | str] = {"data": payload}

        if content_type:
            post_kwargs["content_type"] = content_type

        response = self.client.post(url, **post_kwargs)

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)
        self.assertEqual(TodoList.objects.count(), 0)

    def test_create_list_empty_name(self):
        self._assert_create_list_empty_name("current")

    def test_create_list_empty_name_deprecated(self):
        self._assert_create_list_empty_name("deprecated")

    def _assert_create_list_null_name(self, version: str) -> None:
        payload = {
            "description": "A description for the said todo list",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        url, _, content_type = self.urls_and_expected_status[version]

        post_kwargs: dict[str, dict[str | Any] | str] = {"data": payload}

        if content_type:
            post_kwargs["content_type"] = content_type

        response = self.client.post(url, **post_kwargs)

        self.assertEqual(response.status_code, HTTPStatus.UNPROCESSABLE_ENTITY)

        # Todolist should not be created
        assert TodoList.objects.count() == 0

    def test_create_list_null_name(self):
        self._assert_create_list("current")

    def test_create_list_null_name_deprecated(self):
        self._assert_create_list("deprecated")

    def _assert_create_list_null_description(self, version: str) -> None:
        payload = {
            "title": "Todolist",
            "visibility": True,
        }

        self.client.login(username="test", password=self.users_password)

        url, _, content_type = self.urls_and_expected_status[version]

        post_kwargs: dict[str, dict[str | Any] | str] = {"data": payload}

        if content_type:
            post_kwargs["content_type"] = content_type

        response = self.client.post(self.url, data=payload)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        # List should be created
        assert TodoList.objects.count() == 1
        todolist = TodoList.objects.first()

        assert todolist.title == "Todolist"
        assert todolist.description == ""
        assert todolist.is_public

    def create_list_null_description(self):
        self._assert_create_list_null_description("current")

    def create_list_null_description_deprecated(self):
        self._assert_create_list_null_description("deprecated")

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


class TodoListRead(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test", password=make_password(cls.users_password)
        )
        cls.todolist = TodoListFactory.create(owner=cls.user)
        cls.url = "/todo/lists/{list_id}/"
        cls.public_url = "/todo/lists/public/{list_id}/"

    def test_get_todolist(self):
        self.client.login(username="test", password=self.users_password)
        response = self.client.get(self.url.format(list_id=self.todolist.id))

        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_private_todolist_not_logged(self):
        response = self.client.get(self.public_url.format(list_id=self.todolist.id))

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_get_todolist_wrong_owner(self):
        UserFactory.create(username="test2", password=make_password("1234"))
        self.client.login(username="test2", password=self.users_password)

        response = self.client.get(self.url.format(list_id=self.todolist.id))

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


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
