from pydantic import BaseModel, Field
from typing import List, Optional
from app.db.models.session import Session


class User(BaseModel):
    uid: str = Field(...)
    FCMToken: dict = Field(...)
    email: str = Field(...)
    group: str = Field(...)
    img: str = Field(...)
    name: str = Field(...)
    phone: str = Field(...)
    sessions: List[Session] = []
    profileInfo: dict = Field(None)  # 학생은 처음에 없음!
    availableTime: dict = Field(None)  # 학생만 있음!

    class Config:
        arbitrary_types_allowed = True
