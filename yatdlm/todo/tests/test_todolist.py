from django.test import TestCase
from django.contrib.auth import models as auth_models
from todo.models import TodoList


class TodoListTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = auth_models.User.objects.create_user("test", password="1234")
        cls.other_user = auth_models.User.objects.create_user("test2", password="1234")
        cls.list_ = TodoList(owner=cls.user)
        cls.list_.save()
        cls.url = "/todo/lists/delete/{}"

    def test_delete_list(self):
        list_ = TodoList(owner=self.user)
        list_.save()
        self.client.login(username="test", password="1234")
        response = self.client.delete(self.url.format(list_.id))
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(TodoList.DoesNotExist):
            TodoList.objects.get(id=list_.id)

    def test_delete_list_wrong_user(self):
        list_ = TodoList(owner=self.other_user)
        list_.save()
        self.client.login(username="test", password="1234")
        response = self.client.delete(self.url.format(list_.id))
        self.assertEqual(response.status_code, 403)
        self.assertIsNotNone(TodoList.objects.get(id=list_.id))

    def test_delete_list_user_not_logged(self):
        response = self.client.delete(self.url.format(self.list_.id))
        self.assertEqual(response.status_code, 302)

    def test_delete_list_wrong_verb(self):
        self.client.login(username="test", password="1234")
        response = self.client.post(self.url.format(self.list_.id))
        # Expect a Method not allowed
        self.assertEqual(response.status_code, 405)
        self.assertIsNotNone(TodoList.objects.get(id=self.list_.id))
