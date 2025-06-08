from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Quote:
    """Модель данных для цитаты"""
    _id: str
    author: str
    content: str
    tags: List[str]
    length: Optional[int] = None
    
    def __str__(self) -> str:
        return f'"{self.content}"\n— {self.author}'


@dataclass
class QuoteList:
    """Модель данных для списка цитат"""
    count: int
    totalCount: int
    page: int
    totalPages: int
    lastItemIndex: int
    results: List[Quote]
