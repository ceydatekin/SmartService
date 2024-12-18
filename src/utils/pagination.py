from dataclasses import dataclass
from typing import TypeVar, Generic, List, Optional
from sqlalchemy.orm import Query

T = TypeVar('T')


@dataclass
class PaginationMetadata:
    page: int
    size: int
    total_items: int
    total_pages: int
    has_next: bool
    has_previous: bool


@dataclass
class PaginatedResult(Generic[T]):
    items: List[T]
    metadata: PaginationMetadata


class PaginationParams:
    def __init__(
            self,
            page: int = 0,
            size: int = 10,
            max_size: int = 100,
            min_size: int = 1
    ):
        self.page = max(0, page)
        self.size = max(min_size, min(size, max_size))

    @property
    def offset(self) -> int:
        return self.page * self.size


class QueryPaginator:
    @staticmethod
    def paginate(
            query: Query,
            params: PaginationParams,
            count_query: Optional[Query] = None
    ) -> PaginatedResult[T]:
        """
        Paginates a SQLAlchemy query and returns results with metadata

        Args:
            query: The base query to paginate
            params: Pagination parameters
            count_query: Optional optimized query for counting total items

        Returns:
            PaginatedResult containing items and pagination metadata
        """
        total = count_query.count() if count_query else query.count()

        items = query.offset(params.offset).limit(params.size).all()

        total_pages = (total + params.size - 1) // params.size

        metadata = PaginationMetadata(
            page=params.page,
            size=params.size,
            total_items=total,
            total_pages=total_pages,
            has_next=params.page < total_pages - 1,
            has_previous=params.page > 0
        )

        return PaginatedResult(items=items, metadata=metadata)