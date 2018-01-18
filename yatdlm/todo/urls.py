from django.contrib.auth.decorators import login_required
from django.urls import path


from . import views

urlpatterns = [
    # Default index page
    path('', views.index),
    # Explicit index page
    path('lists', views.index),
    # Specific todo list page
    path('lists/<int:list_id>/', login_required(views.display_list)),
    # Specific todo list _public_ page
    path('lists/public/<int:list_id>/', views.display_list, {'public': True}),
    # Create a new task
    path('lists/<int:list_id>/add_task', views.add_task),
    # Delete a specific task
    path('lists/<int:list_id>/del_task/<int:task_id>', views.del_task),
    # Mark a task as completed (or not)
    path('lists/<int:list_id>/complete_task/<int:task_id>', views.mark_as_done),
    # Display the details of a task
    path('lists/<int:list_id>/detail/<int:task_id>', views.display_detail),
    # Add a followup
    path('lists/<int:list_id>/detail/<int:task_id>/add_followup', views.add_followup),
]