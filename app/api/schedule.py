"""
서버 스케쥴링과 관련된 API. 
2022.06.11 현재 상황
- fastapi 앱 실행 시 스케쥴링 (푸쉬, DB 패치, 등) 수행함.
- 그런데 nginx 에서 돌릴 경우 nginx 가 fastapi 앱 프로세스를 여러개 실행시켜 로드밸런싱 하도록 되어있음
- 그래서 푸쉬, DB 패치 등이 여러번 일어남.
- 그래서 스케쥴링 앱을 따로 돌려서 그 앱이 정해진 시간에 fastapi 서버에 API 콜을 하는 방식으로 구현을 수정할 계획임.
- 06.11 현재 아직 완성 안한상태. (이 스크립트는 현재 쓰이고 있지 않음)
"""

from fastapi import APIRouter
from loguru import logger

from app.core.config import settings
from app.push.reservation_push_handler import ReservationPushHandler

router = APIRouter(tags=["schedule"])


@router.get("/schedule/push/fetch")
async def fetch():
    await ReservationPushHandler.fetch_from_db()
    return "Fetched"


@router.get("/schedule/push/lookup")
def lookup():
    logger.info("hihihih")
    # await ReservationPushHandler.lookup_reservation_db()
    return "Lookup..."


@router.get("/schedule/push/cleanup")
async def cleanup():
    await ReservationPushHandler.cleanup_data()
    return "Cleanup..."


@router.get("/schedule/push/notify/tutors")
async def notify_to_tutors():
    await ReservationPushHandler.notify_to_tutors()
    return "notify to tutors..."


@router.get("/schedule/push/notify/morning")
async def notify_morning():
    await ReservationPushHandler.notify_today_reservation(time="morning")
    return "notify this morning..."


@router.get("/schedule/push/notify/afternoon")
async def notify_afternoon():
    await ReservationPushHandler.notify_today_reservation(time="afternoon")
    return "notify this afternoon..."


@router.get("/schedule/recordings/download-upload")
async def download_and_upload():
    ...
