"""
구글 클라우드 스토리지에 있는 파일들에 접근하는 모듈.
agora cloud recording 이 서드파티 스토리지에 저장하는 것만 제공해서,
현재 세션 녹화본은 구글 클라우드에 저장됐다가 로컬로 가져와서 다시 forbidden 서버에 업로드하는 식으로 관리되고 있음.
"""

from datetime import datetime
import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from google.cloud import storage

from app.utils.async_ftp import AsyncFtpManager
from app.utils.ftp import FtpManager
from app.utils.firestore import FirestoreManager
from app.utils.file import FileManager
from app.core.config import settings


class GoogleCloudMananger:
    def __init__(self, bucket_name, src_blob_path, dst_dir_path):
        self.storage_client = storage.Client()
        self.bucket_name = bucket_name
        self.src_blob_path = src_blob_path
        self.dst_dir_path = dst_dir_path
        self.recordings_today = False

    def setup_schedule(self):
        logger.info("Scheduling Recording Transfer tasks ...")

        sched = AsyncIOScheduler(timezone="Asia/Seoul")

        sched.add_job(self.download_and_upload, "cron", hour=23, minute=30)

        sched.start()

        logger.info("Scheduling Recording Transfer tasks ... Done")

    async def download_and_upload(self):
        # download from storage.
        success = await self.download_from_storage_folder()
        if not self.recordings_today:
            logger.info("No recordings today!!")
            return
        logger.info(f"Completely download recordings from storage?: {success}")

        # upload to NAS server
        dir_path = "./data/recordings/"
        success = self.upload_from_local_folder(dir_path)
        logger.info(f"Completely upload recordings from storage?: {success}")

        # remove local downloaded files
        success = FileManager.remove_files_in_dir(dir_path)
        logger.info(f"Completely remove recordings of local?: {success}")

        # FTP file list 받아와서 firestore 에 저장. (recordings 컬렉션)
        await self.upload_filelist_to_firestore()

    async def upload_filelist_to_firestore(self):

        date = f"{datetime.now().strftime('%Y-%m-%d')}"

        host = settings.FTP_HOST
        port = settings.FTP_PORT
        username = settings.FTP_USERNAME
        password = settings.FTP_PASSWORD
        path = settings.FTP_RECORDING_PATH

        ftp_manager = FtpManager(host, port, username, password, path)

        flist = ftp_manager.file_list(date)

        doc = {"file_list": flist}

        logger.info(f"upload file_list to firestore: {doc}")

        await FirestoreManager.set_document("recordings", date, doc)

    def upload_from_local_folder(self, dir_path):
        host = settings.FTP_HOST
        port = settings.FTP_PORT
        username = settings.FTP_USERNAME
        password = settings.FTP_PASSWORD
        path = settings.FTP_RECORDING_PATH

        ftp_manager = FtpManager(host, port, username, password, path)
        return ftp_manager.upload_dir(dir_path, mkdir=True)

    async def upload_from_local_folder_async(self, dir_path):

        date = f"{datetime.now().strftime('%Y-%m-%d')}"

        host = settings.FTP_HOST
        port = settings.FTP_PORT
        username = settings.FTP_USERNAME
        password = settings.FTP_PASSWORD
        path = settings.FTP_RECORDING_PATH

        async_ftp_manager = AsyncFtpManager()
        await async_ftp_manager.connect(host, port, username, password)

        return await async_ftp_manager.upload_dir(
            path + f"/{date}", dir_path, mkdir=True
        )

    async def download_from_storage_folder(self):
        date = f"{datetime.now().strftime('%Y-%m-%d')}"
        dir_name = f"{datetime.now().strftime('%Y%m%d')}"

        bucket = self.storage_client.get_bucket(self.bucket_name)
        blobs = list(bucket.list_blobs(prefix=f"{self.src_blob_path}{dir_name}/"))

        success = True

        if not blobs:
            logger.info(f"No recordings today. ({dir_name})")
            self.recordings_today = False
            return success

        reservations = await FirestoreManager.get_document(
            collection_name="reservations", document_name=str(date)
        )

        if not reservations:
            logger.info(f"No reservations today.({date})")
            self.recordings_today = False
            return success

        self.recordings_today = True

        filename = ""

        for blob in blobs:
            if blob.name.endswith(".mp4"):
                logger.info(blob.name)
                # get channel_id
                logger.info(blob.name.split("_")[1])

                for channel in reservations:
                    data = reservations[channel]
                    if data["channel_id"] == blob.name.split("_")[1]:
                        try:
                            time_str = "".join(data["time"].split(":"))
                            count = 0
                            filename = f"{data['tutor_uid']}_{data['tutor_name']}_{data['child_name']}_{time_str}_"
                            for fname in os.listdir(self.dst_dir_path):
                                if filename in fname:
                                    count += 1
                            filename = f"{data['tutor_uid']}_{data['tutor_name']}_{data['child_name']}_{time_str}_{count}.mp4"
                            logger.info(self.dst_dir_path + filename)
                            blob.download_to_filename(self.dst_dir_path + filename)
                        except Exception as e:
                            success = False
                            logger.info(
                                f"{e} raised while pulling data from cloud storage."
                            )

        logger.info(
            f"Blobs in {self.src_blob_path}{dir_name}/ downloaded to {self.dst_dir_path}"
        )

        return success
