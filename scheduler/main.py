import asyncio
from datetime import datetime

import aiohttp
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import settings

HOST = settings.HOST
PORT = settings.PORT

date = datetime.now().date()
scheduler = AsyncIOScheduler(timezone="Asia/Seoul")


async def request_to_server(path: str = None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"http://{HOST}:{PORT}/{path}") as resp:
            result = await resp.json()
            print(result)


async def fetch_from_db():
    await request_to_server("/schedule/push/fetch")
    ...


async def notify_today_reservation_morning():
    await request_to_server()
    ...


async def notify_today_reservation_afternoon():
    await request_to_server()
    ...


async def notify_to_tutors():
    await request_to_server()
    ...


async def lookup_reservation_db():
    await request_to_server("/schedule/push/lookup")
    ...
    "세션 시간인지 확인 "


async def cleanup_data():
    await request_to_server("/schedule/push/cleanup")
    ...


async def download_and_upload():
    await request_to_server()
    ...


def setup_schedule(sched: AsyncIOScheduler):

    # reservation

    sched.add_job(
        fetch_from_db,
        "cron",
        hour=7,
        minute=40,
    )

    sched.add_job(notify_today_reservation_morning, "cron", hour=7, minute=50)

    sched.add_job(notify_today_reservation_afternoon, "cron", hour=14, minute=30)

    sched.add_job(notify_to_tutors, "cron", hour=12, minute=30)

    sched.add_job(
        lookup_reservation_db,
        "cron",
        minute=31,
    )

    sched.add_job(
        lookup_reservation_db,
        "cron",
        minute=45,
    )

    sched.add_job(
        cleanup_data,
        "cron",
        hour=23,
        minute=20,
    )

    # google cloud recordings

    sched.add_job(download_and_upload, "cron", hour=23, minute=30)

    sched.start()


if __name__ == "__main__":
    # setup_schedule(sched=scheduler)
    loop = asyncio.get_event_loop()
    loop.create_task(request_to_server("schedule/push/fetch"))
    loop.run_forever()

    # loop = asyncio.get_event_loop()
    # loop.create_task(setup_schedule())
    # loop.run_forever()
