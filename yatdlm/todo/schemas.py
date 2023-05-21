import typing as T

from pydantic import BaseModel, Field


class TaskSchema(BaseModel):
    id: T.Union[int, None]
    title: str
    description: str = Field(alias="descr")
    priority: int
    categories: T.List[int]

    @classmethod
    def _dump_categories(cls: "TaskSchema", obj: T.Any, data: dict) -> None:
        # Pydantic does not have a native compatbility with Django's many to many fields.
        # FIXME: The categories should be a custom schema and this schema should only
        # dump the id using the include keyword argument as detailed here:
        # https://docs.pydantic.dev/latest/usage/exporting_models/
        data["categories"] = [category.id for category in obj.categories.all()]

    @classmethod
    def _dump_description(cls: "TaskSchema", obj: T.Any, data: dict) -> None:
        # The input and output data key for that field is `descr`
        # FIXME: replace `descr` by `description`
        data["descr"] = obj.description

    @classmethod
    def from_orm(cls: "TaskSchema", obj: T.Any):
        # The following fields cannot be copied "as is" and need a custom dumping method
        custom_dump_fields = ["categories", "description"]

        custom_dump_fields_methods = {
            "categories": cls._dump_categories,
            "description": cls._dump_description,
        }

        data = {
            field: getattr(obj, field)
            for field in TaskSchema.__fields__
            if field not in custom_dump_fields
        }

        for field in custom_dump_fields:
            custom_dump_fields_methods[field](obj, data)

        return TaskSchema(**data)

    class Config:
        orm_mode = True
