from pydantic import BaseModel, Field
from datetime import datetime


class Comment(BaseModel):
    bodytext: str = Field(...)
    commenterImg: str = Field(...)
    commenterName: str = Field(...)
    commenterUid: str = Field(...)
    date: datetime = Field(...)

    class Config:
        arbitrary_types_allowed = True
