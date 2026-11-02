import math
from typing import TypeVar, List
from app.schemas.common import PaginatedResponse

T = TypeVar("T")


def paginate(items: List[T], total: int, page: int, page_size: int) -> PaginatedResponse[T]:
    total_pages = math.ceil(total / page_size) if page_size > 0 else 1
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
