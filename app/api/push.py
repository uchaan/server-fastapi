"""
FCM 을 이용한 앱 푸쉬 관련 API
"""

import firebase_admin
from fastapi import APIRouter
from loguru import logger

from app.core.config import settings
from app.push.schema import ChatRequest
from app.push.chat_push_handler import ChatPushHandler
from app.push.reservation_push_handler import ReservationPushHandler


cred = firebase_admin.credentials.Certificate(settings.GOOGLE_APPLICATION_CREDENTIALS)
firebase_admin.initialize_app(cred)


router = APIRouter(tags=["push"])


@router.post("/push/chat-request")
def push_chat_request(item: ChatRequest):
    response = ChatPushHandler.send_message(item, "receive_chat")

    logger.info(f"{item.sender_name}: {item.message}")

    return response


@router.post("/push/reservation/test")
async def test():
    await ReservationPushHandler.lookup_reservation_db()
