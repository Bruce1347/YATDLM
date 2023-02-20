import typing as T

from datetime import datetime
from pydantic import BaseModel, Field

from todo.models import TodoList

class TodoListSchema(BaseModel):
    owner_id: T.Optional[int]
    title: str  = Field("", min_length=1)
    description: str
    is_public: bool = Field(False, alias="visibility")
    creation_date: T.Optional[datetime]
    due_date: T.Optional[datetime]

    class Config:
        _model: TodoList
        attrs: T.List[str] = [
            "owner_id",
            "title",
            "description",
            "is_public",
            "creation_date",
            "due_date",
        ]

    def to_model_instance(self):
        instance_attributes = {
            attr: getattr(self, attr)
            for attr in self.Meta.attrs
        }
        return self.Meta.model(**instance_attributes)