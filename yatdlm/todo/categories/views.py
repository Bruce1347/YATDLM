import json
from http import HTTPStatus

from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods

from ..models import TodoList
from .models import Category
from .schemas import CategoryPatchSchema, CategorySchema


@login_required()
@require_http_methods(["POST"])
def create_category(request, list_id):
    try:
        body = json.loads(request.body.decode("utf-8"))
        category = Category(name=body.get("name"), todolist_id=list_id)
        category.save()
        status_code = 201
        response = CategorySchema.model_validate(category).model_dump()
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
    return JsonResponse(
        {
            "categories": [
                CategorySchema.model_validate(cat).model_dump() for cat in categories
            ]
        }
    )


class CategoryView(View):
    def delete(self, request, category_id, *args, **kwargs):
        qs = Category.objects.filter(id=category_id, todolist__owner_id=request.user.id)

        if not qs.exists():
            return JsonResponse(
                {"errors": "Wrong Category ID"}, status=HTTPStatus.NOT_FOUND
            )

        qs.delete()
        return JsonResponse({}, status=HTTPStatus.OK)

    def patch(self, request, category_id, *args, **kwargs):
        try:
            body = json.loads(request.body.decode("utf-8"))
            schema = CategoryPatchSchema(**body)

            category = Category.objects.get(id=category_id)

            for field, value in schema.model_dump(exclude_unset=True).items():
                setattr(category, field, value)

            category.save()

            return JsonResponse(
                CategorySchema.model_validate(category).model_dump(),
                status=HTTPStatus.OK,
            )
        except Category.DoesNotExist:
            return JsonResponse(
                {"errors": "Wrong Category ID"}, status=HTTPStatus.NOT_FOUND
            )
