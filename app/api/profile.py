"""
사용자 프로필에 관련한 API.
2022.06.11 현재 FireStore DB 를 사용하고 있음. 추후 Mongo DB 로 교체 예정.
"""

import uuid
import os
import pickle

from fastapi import APIRouter, UploadFile
from loguru import logger
import aiofiles

from app.utils.async_ftp import AsyncFtpManager
from app.utils.firestore import FirestoreManager
from app.profile.schema import UserProfile
from app.profile.sns import SnsManager
from app.core.config import settings

router = APIRouter(tags=["profile"])


@router.post("/profile/upload/image")
async def upload_user_image(
    file: UploadFile,
):
    """
    FTP로 forbidden 서버에 이미지 업로드 해줌
    """
    file_name = f"{str(uuid.uuid4())}.png"
    file_path = f"./data/img/{file_name}"

    # save temp file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # get ftp information
    host = settings.FTP_HOST
    port = settings.FTP_PORT
    username = settings.FTP_USERNAME
    password = settings.FTP_PASSWORD
    path = settings.FTP_PROFILE_PATH

    async_ftp_manager = AsyncFtpManager()
    await async_ftp_manager.connect(host, port, username, password)

    success = await async_ftp_manager.upload(path, file_path, file_name)
    logger.info(f"Success on FTP File uploading?: {success}")

    await async_ftp_manager.close()

    if not success:
        return {"file_name": ""}

    # remove temp file after upload
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except:
        logger.info("failed to remove temp img file")

    return {"file_name": file_name}


async def fetch_user_uid_dict():
    """
    신규 유저가 생겼을 경우 로컬(data/users)에 저장된 user-uid 해시맵을 업데이트 해주는 함수
    """
    uid_dict = dict()

    async for doc in FirestoreManager.get_all_documents("users"):
        doc_dict = doc.to_dict()
        uid_dict[doc_dict["uid"]] = doc_dict["name"]

    logger.info(f"new uid_dict: {uid_dict}")
    try:
        with open(f"./data/users/users.pickle", "wb") as f:
            f.write(pickle.dumps(uid_dict))
    except:
        logger.info(f"failed to save uid_dict")


@router.post("/profile/create")
async def create_user_profile(profile: UserProfile):
    profile = profile.dict()["profile"]

    logger.info(profile)

    new_img_url = profile["img"]
    username = profile["name"]
    await SnsManager.update_posts_img(username, new_img_url)
    await FirestoreManager.set_document("users", profile["uid"], profile)

    await fetch_user_uid_dict()


@router.post("/profile/update")
async def update_user_profile(profile: UserProfile):
    profile = profile.dict()["profile"]

    logger.info(profile)

    new_img_url = profile["img"]
    username = profile["name"]
    await SnsManager.update_posts_img(username, new_img_url)
    await FirestoreManager.update_document("users", profile["uid"], profile)


@router.post("/profile/update/test", deprecated=True)
async def update_user_profile(username: str, new_img_url: str):
    await SnsManager.update_posts_img(username, new_img_url)


@router.post("/sns/upload/image")
async def upload_user_image(
    file: UploadFile,
):
    file_name = f"{str(uuid.uuid4())}.png"
    file_path = f"./data/img/{file_name}"

    # save temp file
    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # get ftp information
    host = settings.FTP_HOST
    port = settings.FTP_PORT
    username = settings.FTP_USERNAME
    password = settings.FTP_PASSWORD
    path = settings.FTP_SNS_PATH

    async_ftp_manager = AsyncFtpManager()
    await async_ftp_manager.connect(host, port, username, password)

    success = await async_ftp_manager.upload(path, file_path, file_name)
    logger.info(f"Success on FTP File uploading?: {success}")

    await async_ftp_manager.close()

    # remove temp file after upload
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
    except:
        logger.info("failed to remove temp img file")

    return {"file_name": file_name}


@router.post("/profile/create/test")
async def create_user_profile(
    profile: UserProfile,
    name: str,
    email: str,
    uid: str,
    phone: str,
    grader: str,
    school: str,
    level: int = 1,
):
    profile = profile.dict()["profile"]

    profile["name"] = name
    profile["uid"] = uid
    profile["email"] = email
    profile["img"] = settings.DEFAULT_IMG
    profile["phone"] = phone
    profile["profileInfo"]["grader"] = grader
    profile["profileInfo"]["school"] = school
    profile["profileInfo"]["level"] = "Level1(그림책)" if level == 1 else "Level2(역할극)"

    logger.info(profile)

    await FirestoreManager.set_document("users", profile["uid"], profile)

    return
