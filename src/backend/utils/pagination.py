from backend.models.pagination import Pagination


def calculate_pagination(total: int, page: int, per_page: int) -> Pagination:
    """Calculate pagination parameters"""
    total_pages = (total + per_page - 1) // per_page
    current_page = min(max(page, 1), total_pages)

    return Pagination(
        total=total,
        limit=per_page,
        offset=(current_page - 1) * per_page,
        current_page=current_page,
        has_prev=current_page > 1,
        has_next=current_page < total_pages,
        prev_page=current_page - 1 if current_page > 1 else None,
        next_page=current_page + 1 if current_page < total_pages else None,
        start_index=((current_page - 1) * per_page) + 1,
        end_index=min(current_page * per_page, total),
        page_range=list(
            range(
                max(1, current_page - 2),
                min(total_pages + 1, current_page + 3),
            )
        ),
    )
