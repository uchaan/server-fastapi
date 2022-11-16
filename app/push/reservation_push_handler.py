"""
예약된 세션과 관련한 푸쉬알림을 다루는 모듈.

python FCM 은 아래 링크 참고
https://firebase.google.com/docs/cloud-messaging/send-message#python

"""

import os
import pickle
from datetime import datetime
from datetime import timedelta

import aiofiles
from firebase_admin import messaging
from google.cloud.firestore import AsyncClient
from loguru import logger
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.config import settings
from app.utils.firestore import FirestoreManager


class ReservationPushHandler:
    # FireStore 의 AsyncClient 사용
    db = AsyncClient()
    date = datetime.now().date()

    @classmethod
    def setup_schedule(cls):

        logger.info("Scheduling Reservation notification tasks ...")
        sched = AsyncIOScheduler(timezone="Asia/Seoul")

        sched.add_job(cls.fetch_from_db, "cron", hour=7, minute=45)

        sched.add_job(cls.fetch_from_db, "cron", hour=15, minute=30)

        sched.add_job(
            cls.notify_today_reservation, "cron", hour=7, minute=50, args=["morning"]
        )

        sched.add_job(
            cls.notify_today_reservation, "cron", hour=14, minute=30, args=["afternoon"]
        )

        sched.add_job(cls.notify_to_tutors, "cron", hour=12, minute=30)

        sched.add_job(cls.lookup_reservation_db, "cron", minute=15)

        sched.add_job(cls.lookup_reservation_db, "cron", minute=45)

        sched.add_job(cls.cleanup_data, "cron", hour=23, minute=20)

        sched.start()

        logger.info("Scheduling Reservation notification tasks ... Done.")

        return

    @classmethod
    async def fetch_from_db(cls):
        """
        오늘 날짜에 해당하는 reservation document 를 firestore 로부터 fetch 하고, 로컬에 저장함.
        """
        logger.info("Fetching from firestore DB ...")

        date = datetime.now().date()
        doc_ref = cls.db.collection("reservations").document(str(date))

        doc = await doc_ref.get()
        if doc.exists:
            doc = doc.to_dict()
            # save as .pickle to 'data' folder.
            try:
                async with aiofiles.open(
                    f"./data/reservation/{date}.pickle", "wb"
                ) as f:
                    await f.write(pickle.dumps(doc))
                logger.info(f"fetched reservation data of {date}.")
            except:
                logger.info(f"failed to fetch reservation data of {date}.")
        else:
            doc = dict()
            try:
                async with aiofiles.open(
                    f"./data/reservation/{date}_empty.pickle", "wb"
                ) as f:
                    await f.write(pickle.dumps(doc))
                logger.info(f"no reservation today!")
            except:
                logger.info(f"something wrong with file writing of {date}")
        return

    @classmethod
    def check_fetched(cls):
        """
        오늘 reservation document 가 fetch 되었는지 확인해줌
        """
        date = datetime.now().date()

        is_fetched = os.path.isfile(f"./data/reservation/{date}.pickle")

        if is_fetched:
            return True
        else:
            return False

    @classmethod
    def check_reservation_today(cls):
        """
        오늘 예약되어있는 세션이 있는지 확인
        """
        date = datetime.now().date()

        no_reservation = (
            os.path.isfile(f"./data/reservation/{date}_empty.pickle") == True
        ) and (os.path.isfile(f"./data/reservation/{date}.pickle") == False)

        return False if no_reservation else True

    @classmethod
    def cleanup_data(cls):
        """
        로컬 (data/reservation/) 에 저장된 데이터 모두 삭제
        """
        logger.info("Remove files in /data/reservation ...")
        dname = "./data/reservation"
        for fname in os.listdir(dname):
            fpath = os.path.join(dname, fname)
            try:
                if os.path.isfile(fpath):
                    os.remove(fpath)
            except:
                logger.info(f"failed to remove {fpath}")

        return

    @classmethod
    def is_session_time(cls):
        """
        지금 시간이 세션 활동 시간인지 확인해줌
        """
        current_time = datetime.now()

        session_start_time = current_time.replace(
            hour=int(settings.SESSION_START_TIME_HOUR),
            minute=int(settings.SESSION_START_TIME_MINUTE),
            second=0,
            microsecond=0,
        )

        session_end_time = current_time.replace(
            hour=int(settings.SESSION_END_TIME_HOUR),
            minute=int(settings.SESSION_END_TIME_MINUTE),
            second=0,
            microsecond=0,
        )

        is_session_time = (
            session_start_time < current_time and session_end_time > current_time
        )

        return is_session_time

    @classmethod
    async def push_notification(
        cls, tutor_uid: str, child_uid: str, title, msg, type="session"
    ):
        """
        tutor_uid 와 child_uid 에 푸쉬알림 보냄.
        """
        registration_tokens = []

        if tutor_uid:
            registration_tokens += await cls.get_fcmtoken_in_db(tutor_uid)
        if child_uid:
            registration_tokens += await cls.get_fcmtoken_in_db(child_uid)

        data = dict()
        data["type"] = type
        data["title"] = title
        data["body"] = msg
        data["priority"] = "high"

        message = messaging.MulticastMessage(
            data=data,
            android=messaging.AndroidConfig(priority="high"),
            tokens=registration_tokens,
        )

        response = messaging.send_multicast(message)
        logger.info(f"Pushing reservation notification response: {response}")
        return

    @classmethod
    async def get_fcmtoken_in_db(cls, uid: str):
        """
        uid 에 해당하는 FCM 토큰을 Firestore 로부터 가져옴.
        """
        fcm_tokens = []

        doc_ref = cls.db.collection("users").document(uid)
        doc = await doc_ref.get()
        if doc.exists:
            doc = doc.to_dict()
            fcm_tokens = list(doc["FCMToken"].values())

        return fcm_tokens

    @classmethod
    async def lookup_reservation_db(cls):
        """
        오늘 예정되어있는 세션들을 보고 해당되는 사람들에게 (세션 시작 15분 전에) 푸쉬알림을 보냄.
        """

        if not cls.is_session_time():
            return

        if not cls.check_reservation_today():
            logger.info("No reservation today!!")
            return

        logger.info("It's session time. Look up the today's reservation ...")

        current_time = datetime.now()
        date = current_time.date()

        doc = dict()

        if not cls.check_fetched():
            await cls.fetch_from_db()

        file = f"./data/reservation/{date}.pickle"

        try:
            async with aiofiles.open(file, "rb") as f:
                doc = pickle.loads(await f.read())
        except:
            logger.info("something wrong with file open.")

        if doc:
            for channel in doc:
                data = doc[channel]

                tutor_uid = data["tutor_uid"]
                child_uid = data["child_uid"]
                reservation_time = data["time"]

                tutor_name = data["tutor_name"]
                child_name = data["child_name"]

                channel_start_time_list = reservation_time.split("-")[0].split(":")
                start_hour = str(int(channel_start_time_list[0]) - 12)
                start_min = channel_start_time_list[1]

                start_time = f"오후 {start_hour}시 {start_min}"

                channel_start_time = current_time.replace(
                    hour=int(channel_start_time_list[0]),
                    minute=int(channel_start_time_list[1]),
                    second=0,
                    microsecond=0,
                )

                # 현재 시각이 예약 시간 15분 전 이내인지 확인
                cond1 = current_time + timedelta(minutes=15) >= channel_start_time
                cond2 = current_time <= channel_start_time

                if cond1 and cond2:
                    logger.info(f"push notification to {tutor_name} and {child_name}")
                    await cls.push_notification(
                        tutor_uid=tutor_uid,
                        child_uid=child_uid,
                        title="예약 알림",
                        msg=f"오늘 {start_time}에 예약이 있어요!!",
                    )

        return

    @classmethod
    async def notify_today_reservation(cls, time="morning"):
        """
        오늘 예정된 세션이 있는 사람들에게 오늘 예약이 있음을 알림.
        """

        if not cls.check_reservation_today():
            logger.info("No reservation today!!")
            return

        if not cls.check_fetched():
            await cls.fetch_from_db()

        current_time = datetime.now()
        date = current_time.date()

        file = f"./data/reservation/{date}.pickle"

        try:
            async with aiofiles.open(file, "rb") as f:
                doc = pickle.loads(await f.read())
        except:
            logger.info("something wrong with file open.")

        if doc:
            for channel in doc:
                data = doc[channel]

                tutor_uid = data["tutor_uid"]
                child_uid = data["child_uid"]
                reservation_time = data["time"]

                channel_start_time_list = reservation_time.split("-")[0].split(":")
                start_hour = str(int(channel_start_time_list[0]) - 12)
                start_min = channel_start_time_list[1]

                start_time = f"오후 {start_hour}시 {start_min}"

                if time == "morning":
                    msg = f"좋은 아침이에요! 오늘 예약은 {start_time} 에 시작합니다. 이따 만나요!!"
                else:
                    msg = f"오늘 {start_time}에 있는 예약 잊지 않으셨죠? 이따 만나요!!"

                await cls.push_notification(
                    tutor_uid=tutor_uid, child_uid=child_uid, title="예약 알림", msg=msg
                )

        return

    @classmethod
    async def notify_to_tutors(cls, date: str = None):
        """
        아직 세션 예약 안한 튜터들에게 date 에 헤딩하는 날짜에 n명의 아이들이 예약을 기다린다고 알리기.
        :params date: None 일 경우 오늘 날짜 + 1. 값이 있으면 값에 해당하는 날짜에 대한 예약 현황 체크 후 푸쉬
        """
        if not date:
            date = datetime.now().date()
            today = str(date)
            try:
                tomorrow = str(date.replace(day=date.day + 1))
            except:  # 5/31 -> 6/1, 6/30 -> 7/1 ...
                tomorrow = str(date.replace(month=date.month + 1, day=1))

        # user 데이터 가져오기.
        # 1. Child 수 (n명)
        # 2. 예약 된 child 수 (m명) == 예약 갯수)

        num_child = 0
        async for _ in FirestoreManager.get_documents("users", "group", "student"):
            num_child += 1

        doc_ref_today = cls.db.collection("reservations").document(today)
        doc_ref_tomorrow = cls.db.collection("reservations").document(tomorrow)

        for (doc_ref, date) in [(doc_ref_today, today), (doc_ref_tomorrow, tomorrow)]:
            doc = await doc_ref.get()
            if doc.exists:
                doc = doc.to_dict()

                num_reserved_child = 0
                tutor_reserved = []

                for channel in doc:
                    data = doc[channel]
                    num_reserved_child += 1
                    tutor_reserved.append(data["tutor_uid"])

                date_parsed = date.split("-")

                # msg: 05월11일: 아직 n-m 명의 아이들이 선생님을 기다리고 있어요
                num_child = 34  # 2022년 05월 31일 기준.
                msg = f"{date_parsed[1]}월 {date_parsed[2]}일: 아직 {num_child - num_reserved_child}명의 아이들이 선생님을 기다리고 있어요. 튜터님들의 적극적인 참여 부탁드립니다 !!"

                # reservation 데이터 가져오기.
                # 1. 예약 한 튜터들의 uid 모아놓음.
                # 2. 튜터 그룹에서 예약 안한 튜터들 찾음.
                async for doc in FirestoreManager.get_documents(
                    "users", "group", "tutor"
                ):
                    doc = doc.to_dict()
                    if doc["uid"] not in tutor_reserved:
                        logger.info(f"{doc['uid']} --> ")
                        logger.info(msg)
                        await cls.push_notification(
                            tutor_uid=doc["uid"], child_uid="", title="예약 요청!", msg=msg
                        )

        return
