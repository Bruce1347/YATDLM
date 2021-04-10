import json

from django.contrib.auth import models as auth_models
from django.test import TestCase

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
