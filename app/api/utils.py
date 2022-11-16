"""
사용자 관리, 예약 관리, DB 관리 등에 필요한 유틸리티성 API 콜들을 만들어서 분리해놓은 스크립트.
"""

import pickle

from fastapi import APIRouter
from loguru import logger

from app.push.reservation_push_handler import ReservationPushHandler
from app.utils.firestore import FirestoreManager
from app.utils.ftp import FtpManager
from app.core.config import settings

router = APIRouter(tags=["utils"])


@router.get("/utils/child/time")
async def get_profile_time(uid: str):
    prof = await FirestoreManager.get_document("users", uid)
    return prof["availableTime"]


@router.post("/utils/child/update")
async def update_profile(uid: str, t: dict):
    prof = await FirestoreManager.get_document("users", uid)
    prof["availableTime"] = t

    await FirestoreManager.set_document("users", uid, prof)

    return prof


@router.get("/utils/profile/get")
async def get_user_profile(uid: str):
    user = await FirestoreManager.get_document("users", uid)
    return user


@router.post("/utils/profile/set")
async def set_user_profile(user: dict, uid: str):
    await FirestoreManager.set_document("users", uid, user)
    return


@router.get("/utils/book/get")
async def get_book_from_firestore(uid: str):
    book = await FirestoreManager.get_document("books", uid)
    return book


@router.post("/utils/book/add")
async def add_book_to_firestore(book: dict, uid: str, name: str):
    book["name"] = name
    book["uid"] = uid

    await FirestoreManager.set_document("books", uid, book)

    return book


@router.get("/utils/profile/uid/get")
async def get_uid_from_name(name: str):
    async for doc in FirestoreManager.get_documents("users", "name", name):
        doc_dict = doc.to_dict()
        return doc_dict["uid"]


@router.get("/utils/ftp/flist")
def get_file_list(dirname: str = ""):
    """
    :params dirname: forbidden/crayon/recordings/ + dirname
    e.g.
    dirname = "" 이면 recordings/ 안에 파일이름 리스트 리턴
    dirname = "2022-04-26" 이면 recordings/2022-04-26/ 의 파일이름 리스트 리턴.
    :return: FTP 서버 디렉토리의 파일 리스트
    """

    host = settings.FTP_HOST
    port = settings.FTP_PORT
    username = settings.FTP_USERNAME
    password = settings.FTP_PASSWORD
    path = settings.FTP_RECORDING_PATH

    ftp_manager = FtpManager(host, port, username, password, path)
    return ftp_manager.file_list(dirname)


@router.get("/utils/test/push")
async def test():
    # 내일 예약
    await ReservationPushHandler.push_notification(
    ) # deleted due to the security issue


@router.get("/utils/fetch-reservation-db")
async def fetch():
    await ReservationPushHandler.fetch_from_db()


@router.get("/utils/user-uid-fetch")
async def fetch():
    uid_dict = dict()

    async for doc in FirestoreManager.get_all_documents("users"):
        doc_dict = doc.to_dict()
        uid_dict[doc_dict["uid"]] = doc_dict["name"]

    logger.info(f"uid_dict: {uid_dict}")
    try:
        with open(f"./data/users/users.pickle", "wb") as f:
            f.write(pickle.dumps(uid_dict))
    except:
        logger.info(f"failed to save uid_dict")

    return


@router.get("/utils/test/check-today-reservation")
def read_reservation(date: str):
    """
    :param date: yyyy-mm-dd (2022-05-19)"
    :return: 날짜에 해당하는 reservation document
    """
    try:
        with open("./data/reservation/{date}.pickle", "rb") as f:
            dic = pickle.loads(f.read())
            logger.info(dic)
            return dic
    except:
        logger.info("something wrong with loading reservation")
