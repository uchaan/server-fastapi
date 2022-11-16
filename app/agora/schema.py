import json
from pydantic import BaseModel


class AgoraRequest(BaseModel):
    uid: str
    channel_name: str
    role: int


class RecordingRequest(BaseModel):
    channel_name: str
    student_name: str
    tutor_name: str


class AgoraToken(BaseModel):
    token: str
    code: str

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class AgoraRecorder(BaseModel):
    channel_id: str


class AgoraNewRecorder(BaseModel):
    tutor_name: str
    student_name: str
    channel_id: str
