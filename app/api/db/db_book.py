"""
책 컨텐츠와 관련한 DB APIs
book 스키마는 app/db/models/book.py 참고
"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from app.db.models.book import Book
from app.db.crud.book import BookCrud

router = APIRouter(tags=["db_book"])


@router.post("/db/book/add", response_model=Book)
async def add(book: Book):
    return await BookCrud.add(obj=book, collection_name="books")


@router.get("/db/book/get", response_model=Book)
async def get(uid: str):

    book = await BookCrud.get(id=uid, id_name="uid", collection_name="books")
    if not book:
        raise HTTPException(status_code=404, detail=f"book {uid} not found")
    return book


@router.post("/db/book/update", response_model=Book)
async def update(book: Book):
    updated = await BookCrud.update(
        obj=book, id=book.uid, id_name="uid", collection_name="books"
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"book {book.uid} not found")
    return updated


@router.get("/db/book/delete")
async def delete(uid: str):
    delete_success = await BookCrud.delete(id=uid)
    logger.info(f"deleting book {uid} success? : {delete_success}")
    return delete_success
