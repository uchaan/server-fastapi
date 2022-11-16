"""
앱 내의 세션 리뷰와 관련한 DB APIs
review 스키마는 app/db/models/review.py 참고
"""

from fastapi import APIRouter, HTTPException, Body
from loguru import logger
from typing import List

from app.db.models.review import Review
from app.db.crud.review import ReviewCrud

router = APIRouter(tags=["db_review"])


@router.post("/db/review/add", response_model=Review)
async def add(review: Review):
    return await ReviewCrud.add(r=review, collection_name="reviews")


@router.get("/db/review/get", response_model=Review)
async def get(rid: str):
    review = await ReviewCrud.get(id=rid, id_name="rid", collection_name="reviews")
    if not review:
        raise HTTPException(status_code=404, detail=f"Review {rid} not found")

    return review


@router.post("/db/review/update", response_model=Review)
async def update(review: Review):
    updated_review = await ReviewCrud.update(
        obj=review, id=review.rid, id_name="rid", collection_name="reviews"
    )
    if not updated_review:
        raise HTTPException(status_code=404, detail=f"review {review.rid} not found")

    return updated_review


@router.get("/db/review/delete")
async def delete(rid: str):
    delete_success = await ReviewCrud.delete(
        id=rid, id_name="rid", collection_name="reviews"
    )
    logger.info(f"deleting review {rid} success? : {delete_success}")
    return delete_success
