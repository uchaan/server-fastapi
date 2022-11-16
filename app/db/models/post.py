from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from app.db.models.comment import Comment


class Post(BaseModel):
    pid: Optional[str]  # date + time + poster_uid +
    date: datetime = Field(...)
    bodytext: str = Field(...)
    image: str = Field(...)
    posterImg: str = Field(...)
    posterName: str = Field(...)
    posterUid: str = Field(...)
    showType: int = Field(...)
    reaction: int = 0
    comments: List[Comment] = []
    like: List[str] = []
    amazed: List[str] = []
    angry: List[str] = []
    laugh: List[str] = []
    sad: List[str] = []

    class Config:
        arbitrary_types_allowed = True
