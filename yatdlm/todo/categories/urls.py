from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    # TODO: REMOVE LEGACY ROUTES
    path("<int:category_id>", login_required(views.CategoryView.as_view())),
    path("<int:list_id>/list", views.list_categories, name="list-categories-legacy"),
    path("beta/<int:list_id>", views.list_categories),
    path("<int:list_id>/create", views.create_category),
]
