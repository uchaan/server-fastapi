from pydantic import BaseModel


class User(BaseModel):
    id: str
    name: str
    token: str


class Call(BaseModel):
    call_uuid: str
    channel_id: str
    token: str
    caller: User
    receiver: User


class ChatRequest(BaseModel):
    sender_name: str
    sender_uid: str
    sender_fcm_token: dict
    message: str
    receiver_fcm_token: dict
    receiver_uid: str
