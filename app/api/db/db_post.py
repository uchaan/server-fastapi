"""
앱 내의 SNS 게시물(post)과 관련한 DB APIs
post 스키마는 app/db/models/post.py 참고
"""

from fastapi import APIRouter, HTTPException, Body
from loguru import logger
from typing import List

from app.db.models.post import Post
from app.db.crud.post import PostCrud

router = APIRouter(tags=["db_post"])


@router.post("/db/post/add", response_model=Post)
async def add_post(post: Post):
    return await PostCrud.add(p=post, collection_name="posts")


@router.get("/db/post/get", response_model=Post)
async def get_post(pid: str):
    post = await PostCrud.get(id=pid, id_name="pid", collection_name="posts")
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {pid} not found")

    return post


@router.get("/db/post/get/multiple", response_model=List[Post])
async def get_posts(user_group: str = "all", last_pid: str = None):
    return await PostCrud.get_multiple(
        collection_name="posts", group=user_group, last_pid=last_pid
    )


@router.post("/db/post/update", response_model=Post)
async def update_post(post: Post):
    updated_post = await PostCrud.update(
        obj=post, id=post.pid, id_name="pid", collection_name="posts"
    )
    if not updated_post:
        raise HTTPException(status_code=404, detail=f"post {post.pid} not found")

    return updated_post


@router.post("/db/post/update/url")
async def update_posts(uid: str, img_url: str):
    await PostCrud.update_multiple(uid=uid, img_url=img_url, collection_name="posts")


@router.get("/db/post/delete")
async def delete_post(pid: str):
    delete_success = await PostCrud.delete(
        id=pid, id_name="pid", collection_name="posts"
    )
    logger.info(f"deleting post {pid} success? : {delete_success}")
    return delete_success
