import json
from http import HTTPStatus

from django.contrib.auth import models as auth_models
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from todo.factories import TaskFactory, TodoListFactory, UserFactory
from todo.models import Task, TodoList


class TaskRejectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = auth_models.User.objects.create_user("test", password="1234")
        cls.other_user = auth_models.User.objects.create_user("test2", password="1234")
        cls.list_ = TodoList(owner=cls.user)
        cls.list_.save()
        cls.url = "/todo/lists/{}/{}/reject"

    def test_reject_task(self):
        task = Task(parent_list=self.list_, owner=self.user, priority=Task.NORMAL)
        task.save()
        self.client.login(username="test", password="1234")
        response = self.client.patch(self.url.format(self.list_.id, task.id))
        self.assertEqual(response.status_code, 202)
        task_dict = json.loads(response.content.decode("utf-8"))
        self.assertEqual(task_dict["priority"], Task.REJECTED)

    def test_reject_task_not_owner(self):
        task = Task(parent_list=self.list_, owner=self.user)
        task.save()
        self.client.login(username="test2", password="1234")
        response = self.client.patch(self.url.format(self.list_.id, task.id))
        self.assertEqual(response.status_code, 403)


class TaskUpdateTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = auth_models.User.objects.create_user("test", password="1234")
        cls.other_user = auth_models.User.objects.create_user("test2", password="1234")
        cls.list_ = TodoList(owner=cls.user)
        cls.list_.save()
        cls.url = "/todo/lists/{}/{}/update/"

    def test_update_task(self):
        task = Task(title="Title", parent_list=self.list_, owner=self.user)
        task.save()

        self.client.login(username="test", password="1234")

        data = task.as_dict()
        data["title"] = "Mon super titre"
        data["description"] = "Ma super nouvelle description !"
        response = self.client.patch(
            self.url.format(self.list_.id, task.id), json.dumps(data)
        )
        response_json = response.json()
        self.assertEqual(response.status_code, 202)
        self.assertEqual(response_json["title"], "Mon super titre")

    def test_update_task_wrong_user(self):
        task = Task(title="Title", parent_list=self.list_, owner=self.user)
        task.save()

        self.client.login(username="test2", password="1234")

        data = task.as_dict()

        response = self.client.patch(
            self.url.format(self.list_.id, task.id), json.dumps(data)
        )

        self.assertEqual(response.status_code, 403)


class TaskDelete(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test",
            password=make_password(cls.users_password),
        )
        cls.list_ = TodoListFactory.create(
            owner=cls.user,
        )
        cls.url = "/todo/beta/lists/{list_id}/tasks/{task_id}"

    def test_delete_task(self):
        task = TaskFactory.create(
            parent_list=self.list_,
        )
        task_id = task.id

        self.client.login(username=self.user.username, password=self.users_password)

        response = self.client.delete(
            self.url.format(list_id=self.list_.id, task_id=task.id),
            data={},
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFalse(
            Task.objects.filter(id=task_id, parent_list_id=self.list_.id).exists()
        )

    def test_delete_unknown_task(self):
        self.client.login(username=self.user.username, password=self.users_password)

        response = self.client.delete(
            self.url.format(list_id=self.list_.id, task_id=9999),
            data={},
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

class TaskRead(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test",
            password=make_password(cls.users_password),
        )
        cls.list_ = TodoListFactory.create(
            owner=cls.user,
        )
        cls.task = TaskFactory.create(
            parent_list=cls.list_,
        )
        cls.url = "/todo/beta/lists/{list_id}/tasks/{task_id}?json=true"

    def test_get_task(self):
        self.client.login(username=self.user.username, password=self.users_password)

        response = self.client.get(
            self.url.format(list_id=self.list_.id, task_id=self.task.id),
            data={},
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()
        expected = self.task.as_dict()

        # Pop priorities, the ones in the retrieved payload have their keys as ``str``
        # instead of ``int``.
        # The next two asserts take this fact into account in order to ensure that the
        # retrieved payload is indeed the one generated by the ``as_dict`` method.
        retrieved_priorities: dict = data.pop("priorities")
        db_priorities: dict = expected.pop("priorities")

        self.assertEqual(
            [int(k) for k in retrieved_priorities.keys()],
            [int(k) for k in db_priorities.keys()],
        )

        self.assertEqual(
            sorted(retrieved_priorities.values()),
            sorted(db_priorities.values()),
        )

        self.assertEqual(
            data,
            expected,
        )