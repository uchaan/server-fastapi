"""
앱 내 예약 데이터와 관련하여 MongoDB에 접근하는 CRUD 인터페이스  
"""

from loguru import logger

from app.db.models.reservation import Reservation
from app.db.crud.crud import Crud


class ReservationCrud(Crud):
    @staticmethod
    def put_id(r: Reservation):
        r.rid = r.date + r.channel_id + r.tutor_name + r.child_name
        return r

    @classmethod
    async def add(cls, r: Reservation, collection_name: str):
        r = ReservationCrud.put_id(r)
        return await super().add(r, collection_name)

    @classmethod
    async def get(cls, date: str, collection_name: str):
        """
        get all reservations of input date
        :params date: 포맷 20220401, 20220402, ....
        :return: list of reservations (List<dict>)
        """
        collection = cls.db[collection_name]
        if "-" in date:
            logger.info(
                f"[MongoDB][{collection_name}]\t wrong date format!!, try again (e.g. 20220401(o) 2022-04-01(x))"
            )
            return -1
        return await collection.find({"date": date}).to_list(None)
