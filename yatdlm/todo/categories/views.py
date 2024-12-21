import json

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods

from ..models import TodoList
from .models import Category


@login_required()
@require_http_methods(["POST"])
def create_category(request, list_id):
    try:
        body = json.loads(request.body.decode("utf-8"))
        category = Category(name=body.get("name"), todolist_id=list_id)
        category.save()
        status_code = 201
        response = category.as_dict()
    except IntegrityError:
        status_code = 400
        response = {"error": "The List ID refers to a non existing list."}
    return JsonResponse(response, status=status_code)


@login_required()
@require_http_methods(["GET"])
def list_categories(request, list_id):
    categories = Category.objects.filter(
        todolist_id=list_id, todolist__owner=request.user
    )
    return JsonResponse({"categories": [cat.as_dict() for cat in categories]})


class CategoryView(View):
    def delete(self, request, category_id, *args, **kwargs):
        try:
            category = Category.objects.get(id=category_id)
            category.delete()
            status_code = 200
            response = {"status": "Category deleted"}
        except Category.DoesNotExist:
            status_code = 404
            response = {"errors": "Wrong Category ID"}
        return JsonResponse(response, status=status_code)

    def patch(self, request, category_id, *args, **kwargs):
        try:
            body = json.loads(request.body.decode("utf-8"))
            category = Category.objects.get(id=category_id)
            new_name = body.get("name")
            category.name = new_name
            category.save()
            status_code = 200
            response = category.as_dict()
        except Category.DoesNotExist:
            status_code = 404
            response = {"errors": "Wrong Category ID"}
        except Exception:
            status_code = 500
            response = {"errors": "Unhandled exception"}
        return JsonResponse(response, status=status_code)
