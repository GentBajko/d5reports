from typing import Any, List, Optional

from pydantic import BaseModel


class Pagination(BaseModel):
    order_by: Optional[List[Any]] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
    total: Optional[int] = None
    current_page: Optional[int] = None
    has_prev: Optional[bool] = None
    has_next: Optional[bool] = None
    prev_page: Optional[int] = None
    next_page: Optional[int] = None
    start_index: Optional[int] = None
    end_index: Optional[int] = None
    page_range: Optional[List[int]] = None
