from typing import Generic, TypeVar, List
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    detail: str
    code: str = "ERROR"


class MessageResponse(BaseModel):
    message: str
    detail: str | None = None


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    model_config = ConfigDict(from_attributes=True)
