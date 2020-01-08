from django.test import TestCase
from django.contrib.auth import models as auth_models
from todo.categories.models import Category
from todo.models import TodoList
import json

class CategoryTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = auth_models.User.objects.create_user('test', password='1234')
        cls.list_ = TodoList(owner=cls.user)
        cls.list_.save()

    def setUp(self):
        self.category = Category(name='test_category', todolist=self.list_)
        self.category.save()
        self.client.login(username='test', password='1234')

    def test_patch_category(self):
        response = self.client.patch(
            '/todo/categories/{}'.format(self.category.id),
            json.dumps({"name": "Jon Moxley"}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {"id": 1, "list_id": 1, "name": "Jon Moxley"}, 
            json.loads(response.content))

    def test_patch_non_existent_category(self):
        response = self.client.patch('/todo/categories/1337', json.dumps({}))
        self.assertEqual(response.status_code, 404)

    def test_delete_category(self):
        # Save the ID
        cat_id = self.category.id

        # Confirm that the category is in database
        self.assertIsNotNone(Category.objects.get(id=cat_id))

        # Do the call
        response = self.client.delete('/todo/categories/{}'.format(cat_id))
        self.assertEqual(response.status_code, 200)

        # Check that the category was deleted
        with self.assertRaises(Category.DoesNotExist):
            Category.objects.get(id=cat_id)