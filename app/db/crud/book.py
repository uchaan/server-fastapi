"""
앱 내 책 컨텐츠 데이터와 관련하여 MongoDB에 접근하는 CRUD 인터페이스  
"""

from loguru import logger

from app.db.crud.crud import Crud


class BookCrud(Crud):
    ...
