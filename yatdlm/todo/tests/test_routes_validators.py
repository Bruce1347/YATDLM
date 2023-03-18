from collections import namedtuple
from http import HTTPStatus

from django.http import JsonResponse
from django.test import TestCase

from ..factories import TaskFactory, UserFactory
from ..helpers.routes_validators import task_exists, task_ownership


def dummy_view(request, list_id, task_id, *args, **kwargs):
    return JsonResponse({"foo": "bar"}, status=HTTPStatus.OK)


class TestTaskExistsValidator(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.task = TaskFactory()

    def test_task_exists(self):
        res = task_exists(dummy_view)(object(), self.task.parent_list.id, self.task.id)

        assert isinstance(res, JsonResponse)
        assert res.status_code == HTTPStatus.OK

    def test_task_not_exists(self):
        res = task_exists(dummy_view)(object(), self.task.parent_list.id, 1337)

        assert isinstance(res, JsonResponse)
        assert res.status_code == HTTPStatus.NOT_FOUND


class TestTaskOwnershipValidator(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.task = TaskFactory()
        cls.dummy_request_type = namedtuple("request", "user")

    def test_task_being_owned_by_current_user(self):
        request = self.dummy_request_type(self.task.owner)

        res = task_ownership(dummy_view)(
            request, self.task.parent_list.id, self.task.id
        )

        assert isinstance(res, JsonResponse)
        assert res.status_code == HTTPStatus.OK

    def test_task_not_owned_by_current_user(self):
        request = self.dummy_request_type(UserFactory())

        res = task_ownership(dummy_view)(
            request, self.task.parent_list.id, self.task.id
        )

        assert isinstance(res, JsonResponse)
        assert res.status_code == HTTPStatus.FORBIDDEN


class TestTaskExistsValidatorIntegration(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.task = TaskFactory()

        cls.user = cls.task.owner

        cls.user.set_password("my_super_secret_password")
        cls.user.save()

    def test_get_task(self):
        self.client.login(
            username=self.user.username, password="my_super_secret_password"
        )

        response = self.client.get(
            f"/todo/lists/{str(self.task.parent_list.id)}/{str(self.task.id)}"
        )

        assert response.status_code == HTTPStatus.OK

    def test_get_non_existing_task(self):
        self.client.login(
            username=self.user.username, password="my_super_secret_password"
        )

        response = self.client.get(
            # Tasks PKs are auto incremented ints, here we're chosing an
            # arbitrary id that is high enough to not exist in a test context.
            f"/todo/lists/{str(self.task.parent_list.id)}/{str(420)}"
        )

        assert response.status_code == HTTPStatus.NOT_FOUND


class TestOwnershipValidatorIntegration(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.task = TaskFactory()
        cls.other_user = UserFactory()
        cls.user = cls.task.owner

        cls.user.set_password("my_super_secret_password")
        cls.other_user.set_password("my_super_secret_password_2")
        cls.user.save()
        cls.other_user.save()

    def test_get_task_as_owner(self):
        self.client.login(
            username=self.user.username, password="my_super_secret_password"
        )

        response = self.client.get(
            f"/todo/lists/{str(self.task.parent_list.id)}/{str(self.task.id)}"
        )

        assert response.status_code == HTTPStatus.OK

    def test_get_task_as_other_user(self):
        self.client.login(
            username=self.other_user.username, password="my_super_secret_password_2"
        )

        response = self.client.get(
            f"/todo/lists/{str(self.task.parent_list.id)}/{str(self.task.id)}"
        )

        assert response.status_code == HTTPStatus.FORBIDDEN
