from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

# Index: date
class Reservation(BaseModel):
    rid: Optional[str]  # date + channel_id + tutorname + studentname
    date: str = Field(...)  # 20220401
    time: str = Field(...)  # 16:00-16:30
    formatted_time: datetime = Field(...)  # type 확인 필요!
    channel_id: str = Field(...)
    childBookMark: int = Field(...)
    child_connected: bool = Field(...)
    child_name: str = Field(...)
    child_uid: str = Field(...)
    complete: bool = Field(...)
    tutor_connected: bool = Field(...)
    tutor_name: str = Field(...)
    tutor_uid: str = Field(...)
    bookTitle: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
