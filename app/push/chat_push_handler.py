"""
앱 내 채팅 푸쉬알림를 처리해주는 모듈
"""

import json

from firebase_admin import messaging

from app.push.schema import ChatRequest


class ChatPushHandler:
    @staticmethod
    def send_message(chat_req: ChatRequest, type: str):
        registration_tokens = list(chat_req.receiver_fcm_token.values())

        data = dict()
        data["type"] = type
        data["title"] = chat_req.sender_name
        data["body"] = chat_req.message
        data["uid"] = chat_req.sender_uid
        data["sender_token"] = json.dumps(chat_req.sender_fcm_token)

        message = messaging.MulticastMessage(
            data=data,
            android=messaging.AndroidConfig(priority="high"),
            tokens=registration_tokens,
        )

        return messaging.send_multicast(message)
