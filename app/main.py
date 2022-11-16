"""
FastAPI 실행 스크립트.
FastAPI 앱 실행 시
 - 예약 푸쉬알림 관련 스케쥴링
 - 구글 클라우드 녹화본 처리 관련 스케쥴링
 이 두 가지가 수행됨.
"""

from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.api.agora import router as agora_router
from app.api.push import router as push_router
from app.api.profile import router as profile_router
from app.api.db.db_user import router as db_user_router
from app.api.db.db_reservation import router as db_reservation_router
from app.api.db.db_post import router as db_post_router
from app.api.db.db_book import router as db_book_router
from app.api.db.db_review import router as db_review_router
from app.api.utils import router as utils_router
from app.api.schedule import router as schedule_router
from app.api.firestore.firestore import router as firestore_router
from app.push.reservation_push_handler import ReservationPushHandler
from app.utils.google_cloud import GoogleCloudMananger

app = FastAPI()

app.include_router(agora_router)
app.include_router(push_router)
app.include_router(profile_router)
app.include_router(db_user_router)
app.include_router(db_reservation_router)
app.include_router(db_post_router)
app.include_router(db_book_router)
app.include_router(db_review_router)
app.include_router(utils_router)
app.include_router(schedule_router)
app.include_router(firestore_router)


logger.add(f"logs/logfile.log", rotation="10MB", enqueue=True)


@app.get("/")
def root():
    return "CRAYON server is running ..."


"""
@app.on_event("startup")
def schedule_reservation_push():
    if settings.RESERVATION_PUSH:
        ReservationPushHandler.setup_schedule()

    return


@app.on_event("startup")
async def transfer_recordings():
    if settings.TRANSFER_RECORDINGS:
        google_cloud_manager = GoogleCloudMananger(
            "crayon-cloud-recording", "recordings/", "data/recordings/"
        )
        google_cloud_manager.setup_schedule()

        # await google_cloud_manager.upload_filelist_to_firestore()

    return
"""
