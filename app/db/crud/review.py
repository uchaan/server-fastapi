"""
세션 리뷰와 관련하여 MongoDB 에 접근하는 CRUD 인터페이스
"""

from loguru import logger

from app.db.crud.crud import Crud
from app.db.models.review import Review


class ReviewCrud(Crud):
    @staticmethod
    def put_id(r: Review):
        r.rid = r.date.strftime("%Y%m%d%H%M%S") + r.child_uid + r.tutor_uid
        return r

    @classmethod
    async def add(cls, r: Review, collection_name: str):
        r = ReviewCrud.put_id(r)
        return await super().add(r, collection_name)
