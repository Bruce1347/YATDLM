import json

from django.contrib.auth import models as auth_models
from django.test import TestCase

from todo.categories.models import Category
from todo.models import TodoList

from http import HTTPStatus
from todo.categories.factories import CategoryFactory
from todo.factories import UserFactory


class CategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user: auth_models.User = UserFactory(username="test", set_password="1234")
        cls.todolist = TodoList(owner=cls.user)
        cls.todolist.save()

    def setUp(self):
        self.category = Category(name="test_category", todolist=self.todolist)
        self.category.save()
        self.client.login(username="test", password="1234")

    def test_patch_category(self):
        response = self.client.patch(
            "/todo/categories/{}".format(self.category.id),
            json.dumps({"name": "Science Fiction"}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {
                "id": self.category.id,
                "list_id": self.todolist.id,
                "name": "Science Fiction",
            },
            json.loads(response.content),
        )

    def test_patch_non_existent_category(self):
        response = self.client.patch("/todo/categories/1337", json.dumps({}))
        self.assertEqual(response.status_code, 404)

    def test_delete_category(self):
        # Save the ID
        cat_id = self.category.id

        # Confirm that the category is in database
        self.assertIsNotNone(Category.objects.get(id=cat_id))

        # Do the call
        response = self.client.delete("/todo/categories/{}".format(cat_id))
        self.assertEqual(response.status_code, 200)

        # Check that the category was deleted
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=cat_id)


class CategoryList(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = auth_models.User.objects.create_user("test", password="1234")
        cls.category: Category = CategoryFactory(
            todolist__owner=cls.user,
            name="Science Fiction",
        )

    def test_list_categories(self):
        self.client.login(username="test", password="1234")

        urls = [
            f"/todo/categories/beta/{self.category.todolist.id}",
            # TODO: needs to be removed after legacy cleanup
            f"/todo/categories/{self.category.todolist.id}/list",
        ]

        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(
                {
                    "categories": [
                        {
                            "id": self.category.id,
                            "list_id": self.category.todolist.id,
                            "name": "Science Fiction",
                        }
                    ],
                },
                response.json(),
            )

    def test_list_categories_unlogged(self):
        urls = [
            f"/todo/categories/beta/{self.category.todolist.id}",
            # TODO: needs to be removed after legacy cleanup
            f"/todo/categories/{self.category.todolist.id}/list",
        ]

        for url in urls:
            response = self.client.get(url)
            # Resource has been found but user isn't authenticated.
            # The app redirects to a login page instead.
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_list_categories_other_user(self):
        auth_models.User = UserFactory.create(username="other", set_password="1234")
        self.client.login(username="other", password="1234")

        urls = [
            f"/todo/categories/beta/{self.category.todolist.id}",
            # TODO: needs to be removed after legacy cleanup
            f"/todo/categories/{self.category.todolist.id}/list",
        ]

        for url in urls:
            response = self.client.get(url)
            # Resource has been found but user isn't authenticated.
            # The app redirects to a login page instead.
            self.assertEqual(response.status_code, HTTPStatus.OK)
            self.assertEqual(response.json(), {"categories": []})
