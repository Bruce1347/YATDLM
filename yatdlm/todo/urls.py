from django.urls import path

from . import views

urlpatterns = [
    # Default index page
    path('', views.index),
    # Explicit index page
    path('lists', views.index),
    # Specific todo list page
    path('lists/<int:list_id>/', views.list),
    # Create a new task
    path('lists/<int:list_id>/add_task', views.add_task),
    # Delete a specific task
    path('lists/<int:list_id>/del_task/<int:task_id>', views.del_task)
]