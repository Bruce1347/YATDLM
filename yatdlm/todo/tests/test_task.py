import json
from http import HTTPStatus

from django.contrib.auth import models as auth_models
from django.contrib.auth.hashers import make_password
from django.test import TestCase

from todo.categories.factories import CategoryFactory
from todo.factories import TaskFactory, TodoListFactory, UserFactory
from todo.models import FollowUp, Task, TodoList


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
        cls.url = "/todo/lists/{list_id}/tasks/{task_id}"

    def test_update_task(self):
        task = Task(title="Title", parent_list=self.list_, owner=self.user)
        task.save()

        self.client.login(username="test", password="1234")

        data = task.as_dict()
        data["title"] = "Mon super titre"
        data["description"] = "Ma super nouvelle description !"
        response = self.client.put(
            self.url.format(list_id=self.list_.id, task_id=task.id),
            data,
            content_type="application/json",
        )
        response_json = response.json()
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response_json["title"], "Mon super titre")

    def test_update_categories(self):
        task = TaskFactory.create(
            parent_list=self.list_,
        )
        category = CategoryFactory.create(todolist=self.list_)

        data = task.as_dict()

        data["categories"] = [category.id]

        self.client.login(username="test", password="1234")

        response = self.client.put(
            self.url.format(list_id=self.list_.id, task_id=task.id),
            data,
            content_type="application/json",
        )

        data = response.json()

        self.assertEqual(
            [category.id for category in task.categories.all()],
            [category.id],
        )

    def test_update_categories_wrong_ids(self):
        task = TaskFactory.create(
            parent_list=self.list_,
        )

        data = task.as_dict()

        data["categories"] = [42, 420]

        self.client.login(username="test", password="1234")

        response = self.client.put(
            self.url.format(list_id=self.list_.id, task_id=task.id),
            data,
            content_type="application/json",
        )

        data = response.json()

        self.assertEqual(
            list(task.categories.all()),
            list(),
        )

        # Task has been updated but categories were untouched
        self.assertEqual(
            1,
            FollowUp.objects.count(),
        )

        follow_up = FollowUp.objects.first()

        self.assertEqual(
            follow_up.f_type,
            FollowUp.MODIFICATION,
        )
        self.assertEqual(
            follow_up.writer,
            self.user,
        )
        self.assertEqual(
            follow_up.todol,
            self.list_,
        )
        self.assertEqual(
            follow_up.task,
            task,
        )

    def test_update_task_wrong_user(self):
        task = Task(title="Title", parent_list=self.list_, owner=self.user)
        task.save()

        self.client.login(username="test2", password="1234")

        data = task.as_dict()

        response = self.client.put(
            self.url.format(list_id=self.list_.id, task_id=task.id),
            data,
            content_type="application/json",
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
        cls.url = "/todo/lists/{list_id}/tasks/{task_id}"

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
        cls.url = "/todo/lists/{list_id}/tasks/{task_id}?json=true"

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

    def test_get_unknown_task(self):
        self.client.login(username=self.user.username, password=self.users_password)

        response = self.client.get(
            self.url.format(list_id=self.list_.id, task_id=9999),
            data={},
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_task_wrong_list_id(self):
        self.client.login(username=self.user.username, password=self.users_password)

        response = self.client.get(
            self.url.format(list_id=9999, task_id=self.task.id),
            data={},
        )

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_task_not_logged(self):
        response = self.client.get(
            self.url.format(list_id=self.list_.id, task_id=self.task.id),
            data={},
        )

        self.assertEqual(response.status_code, HTTPStatus.FOUND)


class TaskCreate(TestCase):
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
        cls.url = "/todo/beta/lists/{list_id}/tasks"

    def login(self):
        self.client.login(
            username=self.user.username,
            password=self.users_password,
        )

    def test_create_basic_task(self):
        self.login()

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": "My Task",
                "descr": "My super duper description",
                "priority": Task.NORMAL,
                "categories": [],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        created_task = response.json()

        self.assertIn("id", created_task)

        task = Task.objects.filter(id=created_task.get("id")).first()

        self.assertNotEqual(task, None)

    def test_create_missing_title(self):
        self.login()

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": None,
                "descr": "My super duper description",
                "priority": Task.NORMAL,
                "categories": [],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        recieved_payload = response.json()

        self.assertIn("errors", recieved_payload)

        self.assertEqual(len(recieved_payload["errors"]), 1)

        errors = recieved_payload["errors"][0]

        self.assertEqual(errors["loc"], ["title"])

    def test_create_missing_priority(self):
        self.login()

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": "My super title",
                "descr": "My super duper description",
                "priority": None,
                "categories": [],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        recieved_payload = response.json()

        self.assertIn("errors", recieved_payload)

        self.assertEqual(len(recieved_payload["errors"]), 1)

        errors = recieved_payload["errors"][0]

        self.assertEqual(errors["loc"], ["priority"])

    def test_create_multiple_fields_missing(self):
        self.login()

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": None,
                "descr": "My super duper description",
                "priority": None,
                "categories": [],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        recieved_payload = response.json()

        self.assertIn("errors", recieved_payload)

        self.assertEqual(len(recieved_payload["errors"]), 2)

        # Sort errors alphabetically
        priority_error, title_error = sorted(
            recieved_payload["errors"], key=lambda error: error["loc"][0]
        )

        self.assertEqual(priority_error["loc"], ["priority"])
        self.assertEqual(title_error["loc"], ["title"])

    def test_create_category_does_not_exists(self):
        self.login()

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": "My title",
                "descr": "My super duper description",
                "priority": Task.NORMAL,
                "categories": [42],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
    
    def test_create_multiple_categories_do_not_exists(self):
        self.login()

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": "My title",
                "descr": "My super duper description",
                "priority": Task.NORMAL,
                "categories": [42, 1337],
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)