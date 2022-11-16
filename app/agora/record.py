import json
from datetime import datetime

from loguru import logger
import httpx
import base64

from app.agora.token import TokenHandler
from app.core.config import settings


class Recorder:
    customer_key = settings.AGORA_CUSTOMER_KEY
    customer_secret = settings.AGORA_CUSTOMER_SECRET

    google_cloud_key = settings.GCLOUD_ACCESS_KEY
    google_cloud_secret = settings.GCLOUD_SECRET

    credentials = customer_key + ":" + customer_secret
    base64_credentials = base64.b64encode(credentials.encode("utf8"))
    credential = base64_credentials.decode("utf8")

    # create header obj
    headers = {}

    headers["Authorization"] = "basic " + credential
    headers["Content-Type"] = "application/json"

    @classmethod
    async def acquire(cls, channel_name, uid):
        """
        Get a resource ID
        """
        app_id = TokenHandler.app_id

        url = f"https://api.agora.io/v1/apps/{app_id}/cloud_recording/acquire"

        body = {"cname": channel_name, "uid": uid, "clientRequest": {}}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url, headers=cls.headers, data=json.dumps(body)
            )

        return response.text

    @classmethod
    async def start(cls, channel_name, uid, resource_id):
        """
        Start recording of given resource ID
            - Composite Recording
            - HD (1280 x 720)
            - Storage: Google Cloud
        """
        app_id = TokenHandler.app_id
        _token = TokenHandler.get_token(channel_name, uid)

        dir_name = f"{datetime.now().strftime('%Y%m%d')}"
        url = f"https://api.agora.io/v1/apps/{app_id}/cloud_recording/resourceid/{resource_id}/mode/mix/start"

        logger.info(f"channel_name of recording: {channel_name}")

        # https://docs.agora.io/en/cloud-recording/video_profile_web_ng

        body = {
            "cname": channel_name,
            "uid": uid,
            "clientRequest": {
                "token": _token,
                "storageConfig": {
                    "secretKey": cls.customer_secret,
                    "vendor": 6,  # Google Cloud
                    "region": 0,
                    "bucket": "crayon-cloud-recording",
                    "accessKey": cls.google_cloud_key,
                    "secretKey": cls.google_cloud_secret,
                    "fileNamePrefix": ["recordings", dir_name],
                },
                "recordingConfig": {
                    "maxIdleTime": 5,  # leave channel if no users for 5 secs
                    "transcodingConfig": {  # 480p
                        "height": 480,
                        "width": 640,
                        "bitrate": 500,
                        "fps": 15,
                        "mixedVideoLayout": 1,
                    },
                },
                "recordingFileConfig": {
                    "avFileType": ["hls", "mp4"]
                },  # default: hls. "mp4" makes it to create mp4 file.
            },
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=url, headers=cls.headers, data=json.dumps(body)
            )

        return response.text

    @classmethod
    def query(cls):
        """
        Query recording status
        """
        pass

    @classmethod
    def stop(cls, channel_name, uid, recording_id, start_id):
        """
        Stop recording
        """
        pass
