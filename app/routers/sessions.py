import logging
from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, Query
from app.auth.dependencies import get_current_user
from app.models.session import Session
from app.models.user import User
from app.routers._session_helpers import get_user_session, to_session_list_response, to_session_response
from app.schemas.session import SessionCreate, SessionListItemResponse, SessionResponse, SessionUpdate

logger = logging.getLogger("mytraining")
router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("", response_model=list[SessionListItemResponse], response_model_by_alias=True)
async def list_sessions(
    date: datetime | None = None,
    from_: datetime | None = Query(None, alias="from"),
    to: datetime | None = None,
    limit: int = 100,
    skip: int = 0,
    current_user: User = Depends(get_current_user),
):
    query: dict = {"user_id": str(current_user.id)}
    if date:
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        query["date"] = {"$gte": start, "$lte": end}
    elif from_ or to:
        date_query: dict = {}
        if from_:
            date_query["$gte"] = from_
        if to:
            date_query["$lte"] = to
        query["date"] = date_query

    sessions = await Session.find(query, fetch_links=True).skip(skip).limit(limit).to_list()
    return [to_session_list_response(s) for s in sessions]


@router.get("/{id}", response_model=SessionResponse, response_model_by_alias=True)
async def get_session(id: str, current_user: User = Depends(get_current_user)):
    await get_user_session(id, current_user)
    session = await Session.get(PydanticObjectId(id), fetch_links=True)
    return to_session_response(session)


@router.post("", response_model=SessionResponse, response_model_by_alias=True, status_code=201)
async def create_session(body: SessionCreate, current_user: User = Depends(get_current_user)):
    session = Session(
        user_id=str(current_user.id),
        **body.model_dump(),
    )
    await session.insert()
    logger.info(f"Session {session.id} created by user {current_user.id}")
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)


@router.put("/{id}", response_model=SessionResponse, response_model_by_alias=True)
async def update_session(id: str, body: SessionUpdate, current_user: User = Depends(get_current_user)):
    session = await get_user_session(id, current_user)
    update_data = body.model_dump(exclude_none=True)
    if update_data:
        update_data["updated_at"] = datetime.utcnow()
        await session.set(update_data)
    logger.info(f"Session {id} updated")
    session = await Session.get(PydanticObjectId(id), fetch_links=True)
    return to_session_response(session)


@router.delete("/{id}", status_code=204)
async def delete_session(id: str, current_user: User = Depends(get_current_user)):
    session = await get_user_session(id, current_user)
    await session.delete()
    logger.info(f"Session {id} deleted by user {current_user.id}")
