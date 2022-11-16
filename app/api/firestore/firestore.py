"""
Firestore 에 저장된 데이터 가져오기 위한 api
"""

from fastapi import APIRouter
from loguru import logger

from app.utils.firestore import FirestoreManager
from app.db.crud.post import PostCrud
from app.db.crud.review import ReviewCrud

from app.db.models.post import Post
from app.db.models.review import Review


router = APIRouter(tags=["firestore"])


@router.get("/firestore/user/get")
async def get_user_with_name(uid: str):
    return await FirestoreManager.get_document("users", uid)


@router.get("/firestore/reservation/get")
async def get_reservations_list(date: str):
    return await FirestoreManager.get_document("reservations", date)


@router.get("/firestore/post/get")
async def get_post(pid: str):
    return await FirestoreManager.get_document("posts", pid)


@router.get("/firestore/post/transfer")
async def transfer_all_data_to_mongo():
    async for doc in FirestoreManager.get_all_documents("posts"):
        doc = doc.to_dict()
        logger.info(f"add post to Mongo...")
        await PostCrud.add(Post.parse_obj(doc))


@router.get("/firestore/book/get")
async def get_book(uid: str):
    return await FirestoreManager.get_document("books", uid)


@router.get("/firestore/book/get/words")
async def get_words(uid: str):
    dic = dict()
    async for doc in FirestoreManager.get_subcollection_document("books", uid, "words"):
        dic[doc.id] = doc.to_dict()

    return dic


@router.get("/firestore/review/get")
async def get_review(rid: str):
    return await FirestoreManager.get_document("review", rid)


@router.get("/firestore/review/transfer")
async def transfer_review():
    async for doc in FirestoreManager.get_all_documents("review"):
        await ReviewCrud.add(Review.parse_obj(doc.to_dict()))
