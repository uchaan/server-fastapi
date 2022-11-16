import time

from loguru import logger

from app.agora.lib.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from app.core.config import settings


class TokenHandler:
    app_id = settings.AGORA_APP_ID
    app_cert = settings.AGORA_APP_CERT

    @classmethod
    def get_token(cls, channel_name, uid) -> str:
        exp_time_in_secs = 6000
        current_ts = int(time.time())
        privilege_exp_ts = current_ts + exp_time_in_secs

        token = RtcTokenBuilder.buildTokenWithAccount(
            cls.app_id,
            cls.app_cert,
            channel_name,
            uid,
            Role_Attendee,
            privilege_exp_ts,
        )

        # logger.info(f"Token generated with user_id: {token}")

        return token
