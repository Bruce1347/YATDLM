from django.contrib.auth.decorators import login_required
from django.urls import include, path

from . import views

urlpatterns = [
    # Default index page
    path("", views.index, {"xhr": False}),
    # Explicit index page
    path("lists", views.index, {"xhr": False}),
    # Add a new todo list
    path("lists/add", views.add_list),
    # Specific todo list page
    path("lists/<int:list_id>/", login_required(views.display_list)),
    path("lists/<int:list_id>/tasks", views.list_tasks),
    # Specific todo list _public_ page
    path("lists/public/<int:list_id>/", views.display_list, {"public": True}),
    # Specific task public page
    path("lists/public/<int:list_id>/<int:task_id>", views.display_task_public),
    # Delete a list
    path("lists/delete/<int:list_id>", views.delete_list),
    # Create a new task
    path("lists/<int:list_id>/add_task", views.add_task),
    # Delete a specific task
    path("lists/<int:list_id>/del_task/<int:task_id>", views.delete_task),
    # Display the details of a task
    path("lists/<int:list_id>/detail/<int:task_id>", views.display_detail),
    # Update a task
    path("lists/<int:list_id>/<int:task_id>/update/", views.update_task),
    # Close a task
    path("lists/<int:list_id>/<int:task_id>/close", views.close_task),
    # Add a followup
    path("lists/<int:list_id>/<int:task_id>/add_followup", views.add_followup),
    # Get all followups
    path("lists/<int:list_id>/<int:task_id>/get_followups", views.get_followups),
    path("lists/<int:list_id>/<int:task_id>/reject", views.reject_task),
    path("lists/<int:list_id>/<int:task_id>", views.display_task),
    path("categories/", include("todo.categories.urls")),
    path(
        "beta/lists/<int:list_id>/tasks/<int:task_id>",
        views.TaskView.as_view(),
    ),
]
