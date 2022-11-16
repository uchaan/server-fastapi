from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class Review(BaseModel):
    rid: Optional[str]  # Review ID
    character: str = Field(...)
    childActivity: str = Field(...)
    child_uid: str = Field(...)
    closing: str = Field(...)
    conversation: str = Field(...)
    date: datetime = Field(...)
    happyPoint: str = Field(...)
    honeytip: str = Field(...)
    opening: str = Field(...)
    tutorActivity: str = Field(...)
    tutor_uid: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
