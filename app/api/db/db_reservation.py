"""
앱 내의 세션 예약과 관련한 DB APIs
reservation 스키마는 app/db/models/reservation.py 참고
"""

from fastapi import APIRouter, HTTPException
from loguru import logger
from typing import List

from app.db.models.reservation import Reservation
from app.db.crud.reservation import ReservationCrud

router = APIRouter(tags=["db_reservation"])


@router.post("/db/reservation/add", response_model=Reservation)
async def add_reservation(reservation: Reservation):
    return await ReservationCrud.add(reservation, collection_name="reservations")


@router.get("/db/reservation/get", response_model=List[Reservation])
async def get_reservations_of_date(date: str):
    reservations_list = await ReservationCrud.get(
        date=date, collection_name="reservations"
    )
    if reservations_list == -1:
        raise ValueError(f"wrong date format ({date}). Try again (YYYYMMDD)")
    return reservations_list


@router.post("/db/reservation/update", response_model=Reservation)
async def update_reservation(reservation: Reservation):
    updated = await ReservationCrud.update(
        obj=reservation,
        id=reservation.rid,
        id_name="rid",
        collection_name="reservations",
    )
    if not updated:
        raise HTTPException(status_code=404, detail=f"user {reservation.rid} not found")

    return updated


@router.get("/db/reservation/delete")
async def delete_reservation(rid: str):
    """
    :param rid: date + channel_id + tutorname + childname (e.g. 20220416Ktasnlcma2김아무개최아무개)
    :return: delete 성공 여부
    """

    delete_success = await ReservationCrud.delete(
        id=rid, id_name="rid", collection_name="reservations"
    )
    logger.info(f"deleting user {rid} success? : {delete_success}")
    return delete_success
