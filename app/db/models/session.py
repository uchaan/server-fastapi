from pydantic import BaseModel, Field
from datetime import datetime


class Session(BaseModel):
    date: datetime = Field(...)
    done: bool = Field(...)
    uid: str = Field(...)

    class Config:
        arbitrary_types_allowed = True
