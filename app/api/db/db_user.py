"""
앱 사용자 정보와 관련한 DB APIs
user 스키마는 app/db/models/user.py 참고
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.db.models.user import User
from app.db.crud.user import UserCrud

router = APIRouter(tags=["db_user"])


@router.post("/db/user/add", response_model=User)
async def add_user(user: User):
    return await UserCrud.add(obj=user, collection_name="users")


@router.get("/db/user/get", response_model=User)
async def get_user(uid: str):

    user = await UserCrud.get(id=uid, id_name="uid", collection_name="users")
    if not user:
        raise HTTPException(status_code=404, detail=f"user {uid} not found")
    return user


@router.post("/db/user/update", response_model=User)
async def update_user(user: User):
    updated_user = await UserCrud.update(
        obj=user, id=user.uid, id_name="uid", collection_name="users"
    )
    if not updated_user:
        raise HTTPException(status_code=404, detail=f"user {user.uid} not found")
    return updated_user


@router.get("/db/user/delete")
async def delete_user(uid: str):
    delete_success = await UserCrud.delete(
        id=uid, id_name="uid", collection_name="users"
    )
    logger.info(f"deleting user {uid} success? : {delete_success}")
    return delete_success
