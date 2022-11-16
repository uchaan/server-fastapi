from pydantic import BaseModel, Field
from typing import List, Optional


class Room(BaseModel):
    class Config:
        arbitrary_types_allowed = True
