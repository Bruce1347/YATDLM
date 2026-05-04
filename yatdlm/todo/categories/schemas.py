from pydantic import BaseModel, Field


class CategorySchema(BaseModel):
    id: int
    list_id: int = Field(validation_alias="todolist_id")
    name: str

    model_config = {"from_attributes": True}


class CategoryPatchSchema(BaseModel):
    name: str | None = None

    model_config = {"extra": "ignore"}
