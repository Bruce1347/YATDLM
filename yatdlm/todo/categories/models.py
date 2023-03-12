from django.db import models
from django.contrib import admin


class Category(models.Model):
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    todolist = models.ForeignKey("todo.TodoList", on_delete=models.CASCADE, null=False)

    name = models.CharField(max_length=64)

    def as_dict(self):
        return {"id": self.id, "list_id": self.todolist_id, "name": self.name}

    def __str__(self):
        return self.name


class CategoryAdmin(admin.ModelAdmin):
    pass
