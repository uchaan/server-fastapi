from pydantic import BaseModel, Field
from typing import List, Optional


class BookInfo(BaseModel):
    iterationNum: int = Field(...)
    level: int = Field(...)
    pages: int = Field(...)
    title: str = Field(...)


class Book(BaseModel):
    uid: str = Field(...)
    name: str = Field(...)
    booklist: List[BookInfo] = []
    words: dict = Field(...)

    class Config:
        arbitrary_types_allowed = True
