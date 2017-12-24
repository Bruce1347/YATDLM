from django.urls import path

from . import views

urlpatterns = [
    # Default index page
    path('', views.index),
    # Explicit index page
    path('lists', views.index),
    # Specific todo list page
    path('lists/<int:list_id>/', views.list),
]