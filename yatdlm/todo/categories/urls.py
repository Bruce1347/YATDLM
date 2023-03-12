from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("<int:list_id>/create", views.create_category),
    path("<int:list_id>/list", views.list_categories),
    path("<int:category_id>", login_required(views.CategoryView.as_view())),
]
