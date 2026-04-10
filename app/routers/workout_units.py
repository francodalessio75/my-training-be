import logging
from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.models.session import Session, WorkoutUnit
from app.models.training_type import TrainingType
from app.models.user import User
from app.routers._session_helpers import get_user_session, to_session_response
from app.schemas.common import ReorderRequest, raise_not_found
from app.schemas.session import SessionResponse
from app.schemas.workout_unit import WorkoutUnitCreate, WorkoutUnitUpdate

logger = logging.getLogger("mytraining")
router = APIRouter(tags=["workout-units"])


@router.post("/sessions/{session_id}/units", response_model=SessionResponse, response_model_by_alias=True, status_code=201)
async def add_unit(session_id: str, body: WorkoutUnitCreate, current_user: User = Depends(get_current_user)):
    session = await get_user_session(session_id, current_user)
    tt = await TrainingType.get(PydanticObjectId(body.training_type_id))
    if tt is None:
        raise_not_found("TrainingType")

    unit = WorkoutUnit(
        training_type=tt,
        total_load_description=body.total_load_description,
        notes=body.notes,
    )
    session.workout_units.append(unit)
    session.updated_at = datetime.utcnow()
    await session.save()
    logger.info(f"WorkoutUnit {unit.id} added to Session {session_id}")
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)


@router.put("/sessions/{session_id}/units/{unit_id}", response_model=SessionResponse, response_model_by_alias=True)
async def update_unit(
    session_id: str, unit_id: str, body: WorkoutUnitUpdate, current_user: User = Depends(get_current_user)
):
    session = await get_user_session(session_id, current_user)
    unit = next((u for u in session.workout_units if str(u.id) == unit_id), None)
    if unit is None:
        raise_not_found("WorkoutUnit")

    if body.total_load_description is not None:
        unit.total_load_description = body.total_load_description
    if body.notes is not None:
        unit.notes = body.notes
    if body.training_type_id is not None:
        tt = await TrainingType.get(PydanticObjectId(body.training_type_id))
        if tt is None:
            raise_not_found("TrainingType")
        unit.training_type = tt

    session.updated_at = datetime.utcnow()
    await session.save()
    logger.info(f"WorkoutUnit {unit_id} updated in Session {session_id}")
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)


@router.delete("/sessions/{session_id}/units/{unit_id}", status_code=204)
async def delete_unit(session_id: str, unit_id: str, current_user: User = Depends(get_current_user)):
    session = await get_user_session(session_id, current_user)
    original_len = len(session.workout_units)
    session.workout_units = [u for u in session.workout_units if str(u.id) != unit_id]
    if len(session.workout_units) == original_len:
        raise HTTPException(status_code=404, detail="WorkoutUnit not found.")
    session.updated_at = datetime.utcnow()
    await session.save()
    logger.info(f"WorkoutUnit {unit_id} deleted from Session {session_id}")


@router.patch("/sessions/{session_id}/units/reorder", response_model=SessionResponse, response_model_by_alias=True)
async def reorder_units(
    session_id: str, body: ReorderRequest, current_user: User = Depends(get_current_user)
):
    session = await get_user_session(session_id, current_user)
    unit_map = {str(u.id): u for u in session.workout_units}
    session.workout_units = [unit_map[id] for id in body.ordered_ids if id in unit_map]
    session.updated_at = datetime.utcnow()
    await session.save()
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)
