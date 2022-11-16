"""
agora (세션 토큰 발행, 세션 녹화) 와 관련한 API
"""

import pickle
import json

from http import HTTPStatus
from fastapi import APIRouter
from loguru import logger

from app.agora.schema import (
    AgoraRequest,
    AgoraToken,
    RecordingRequest,
)
from app.agora.token import TokenHandler
from app.agora.record import Recorder

router = APIRouter(tags=["agora"])

uid_dict = dict()

try:
    with open("./data/users/users.pickle", "rb") as f:
        uid_dict = pickle.loads(f.read())
        logger.info("successfully load uid_dict from ./data/users/users.pickle")
except:
    logger.info("something wrong with loading uid_dict")


@router.post("/agora/token", response_model=AgoraToken)
def generate_token(item: AgoraRequest):
    if uid_dict:
        try:
            name = uid_dict[item.uid]
            logger.info(f"{name} entered to call session.")
        except:
            _token = TokenHandler.get_token(item.channel_name, item.uid)
            return AgoraToken(token=_token, code=HTTPStatus.OK)

    _token = TokenHandler.get_token(item.channel_name, item.uid)
    return AgoraToken(token=_token, code=HTTPStatus.OK)


@router.post("/agora/acquire-resource-id")
async def acquire(channelname: str):
    uid = 999
    return await Recorder.acquire(channel_name=channelname, uid=str(uid))


@router.post("/agora/start-cloud-recording")
async def start_recording(item: RecordingRequest):
    """
    아고라 통화 채널의 녹화를 시작시킴.
    agora cloud recording API 의 acquire() 과 start() 를 사용함.
    녹화된 영상은 google cloud storage 의 crayon-cloud-recording/recordings/{date} 에 업로드됨
    """

    uid = 999

    response_acquire = await Recorder.acquire(item.channel_name, uid=str(uid))

    response_acquire = json.loads(response_acquire)

    resource_id = response_acquire["resourceId"]

    response_start = await Recorder.start(
        item.channel_name,
        uid=str(uid),
        resource_id=resource_id,
    )

    return response_start


@router.post("/agora/stop-cloud-recording", deprecated=True)
async def stop_recording():
    ...
