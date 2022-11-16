from pydantic import BaseModel


class UserProfile(BaseModel):
    profile: dict
