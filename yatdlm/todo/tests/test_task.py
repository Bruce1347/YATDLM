from django.test import TestCase
from django.contrib.auth import models as auth_models
from todo.models import TodoList, Task
import copy
import json

class TaskRejectTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = auth_models.User.objects.create_user('test', password='1234')
        cls.other_user = auth_models.User.objects.create_user('test2', password='1234')
        cls.list_ = TodoList(owner=cls.user)
        cls.list_.save()
        cls.url = '/todo/lists/{}/{}/reject'

    def test_reject_task(self):
        task = Task(parent_list=self.list_, owner=self.user, priority=Task.NORMAL)
        task.save()
        self.client.login(username='test', password='1234')
        response = self.client.patch(self.url.format(self.list_.id, task.id))
        self.assertEqual(response.status_code, 202)
        task_dict = json.loads(response.content.decode("utf-8"))
        self.assertEqual(task_dict["priority"], Task.REJECTED)

    def test_reject_task_not_owner(self):
        task = Task(parent_list=self.list_, owner=self.user)
        task.save()
        self.client.login(username='test2', password='1234')
        response = self.client.patch(self.url.format(self.list_.id, task.id))
        self.assertEqual(response.status_code, 403)
