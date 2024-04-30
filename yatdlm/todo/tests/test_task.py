import json
from datetime import datetime
from http import HTTPStatus
from typing import Any

import freezegun
from django.contrib.auth import models as auth_models
from django.contrib.auth.hashers import make_password
from django.test import TestCase
from todo.categories.factories import CategoryFactory
from todo.factories import TaskFactory, TodoListFactory, UserFactory
from todo.models import FollowUp, Task, TodoList
from todo.schemas import TaskSchema

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
        self.assertEqual(task.owner, self.user)

    def test_create_task_correct_task_number(self):
        TaskFactory(
            parent_list=self.list_,
            owner=self.user,
        )

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

        # Should be 2nd task in the list
        self.assertEqual(created_task["task_no"], 2)

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

    def test_create_subtask(self):
        self.login()

        parent_task = TaskFactory(
            parent_list=self.list_,
            owner=self.user,
        )

        response = self.client.post(
            self.url.format(list_id=self.list_.id),
            data={
                "title": "My title",
                "descr": "My super duper description",
                "priority": Task.NORMAL,
                "categories": [],
                "parent_task_id": parent_task.id,
            },
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        self.assertEqual(
            Task.objects.filter(parent_task_id=parent_task.id).count(),
            1,
        )

        data: dict[str, Any] = response.json()

        task = Task.objects.filter(id=data["id"]).first()

        self.assertIsNotNone(task)

        self.assertEqual(task.parent_task, parent_task)


class TasksList(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.users_password = "1234"
        cls.user = UserFactory.create(
            username="test",
            password=make_password(cls.users_password),
        )
        cls.other_user = UserFactory.create(
            username="other_user",
            password=make_password(cls.users_password),
        )
        cls.list_ = TodoListFactory.create(
            owner=cls.user,
        )
        cls.url = f"/todo/beta/lists/{cls.list_.id}/tasks"
        cls.tasks: list[Task] = TaskFactory.create_batch(
            3,
            parent_list=cls.list_,
            owner=cls.user,
        )

    def login(self, user_to_log):
        self.client.login(
            username=user_to_log,
            password=self.users_password,
        )

    def test_get_task(self):
        self.login(self.user)

        response = self.client.get(
            self.url,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()

        self.assertIsNotNone(data["tasks"])
        self.assertIsInstance(data["tasks"], list)
        self.assertEqual(len(data["tasks"]), 3)

    def test_get_task_no_ownership(self):
        self.login(self.other_user)

        response = self.client.get(
            self.url,
        )

        # The following request might be legitimate since lists have autoincremented int as ids.
        # However a user that does not have the ownership of the list should not be able to see its tasks.
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = response.json()

        self.assertIsNotNone(data["tasks"])
        self.assertIsInstance(data["tasks"], list)
        self.assertEqual(len(data["tasks"]), 0)


class RejectTask(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.user_password = "1234"
        cls.user = UserFactory.create(
            username="test",
            password=make_password(cls.user_password),
        )

        cls.todo_list: TodoList = TodoListFactory.create(
            owner=cls.user,
        )
        cls.task: Task = TaskFactory.create(
            parent_list=cls.todo_list,
            owner=cls.user,
        )
        cls.url = f"/todo/lists/{cls.todo_list.id}/tasks/{cls.task.id}"

    def login(self, user_to_log):
        self.client.login(
            username=user_to_log,
            password=self.user_password,
        )

    def test_basic(self):
        self.login(self.user)

        payload = TaskSchema.from_orm(self.task).model_dump()

        payload["rejected"] = True

        response = self.client.patch(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)

        task = Task.objects.filter(id=self.task.id).first()

        self.assertEqual(task.priority, Task.REJECTED)
        self.assertTrue(
            FollowUp.objects.filter(
                old_priority=Task.NORMAL,
                new_priority=Task.REJECTED,
                writer=self.user,
                task=self.task,
                todol=self.todo_list,
            )
        )

    def test_reject_not_owner(self):
        other_user: auth_models.User = auth_models.User.objects.create_user(
            "test2",
            password=self.user_password,
        )

        self.login(other_user)

        payload = TaskSchema.from_orm(self.task).model_dump()

        response = self.client.patch(
            self.url,
            data=payload,
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)


class TaskFollowup(TestCase):
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
        cls.task: Task = TaskFactory.create(
            parent_list=cls.list_,
            owner=cls.user,
        )
        cls.url = f"/todo/lists/{cls.list_.id}/tasks/{cls.task.id}/followups"

    def login(self):
        self.client.login(
            username=self.user.username,
            password=self.users_password,
        )

    @freezegun.freeze_time()
    def test_create_followup(self):
        self.login()

        response = self.client.post(
            self.url,
            data={"followup": f"I'm a followup comment for task {self.task.id}"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, HTTPStatus.CREATED)
        self.assertTrue(
            FollowUp.objects.filter(
                task_id=self.task.id, todol_id=self.list_.id
            ).exists()
        )

        self.assertEqual(
            response.json(),
            {
                "task_id": self.task.id,
                "todol_id": self.list_.id,
                "content": f"I'm a followup comment for task {self.task.id}",
                "new_priority": None,
                "old_priority": None,
                "writer": str(self.user),
                "f_type": "COMMENT",
                # Ids are autoincremented, there should be only one followup
                "id": 1,
                # Time is frozen by freeze gun, no worries about using ``now``
                "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
        )
