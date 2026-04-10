import logging
from datetime import datetime
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.session import ExecutedSet, Session
from app.models.user import User
from app.routers._session_helpers import get_user_session, to_session_response
from app.schemas.common import ReorderRequest, raise_not_found
from app.schemas.executed_set import ExecutedSetCreate, ExecutedSetUpdate
from app.schemas.session import SessionResponse

logger = logging.getLogger("mytraining")
router = APIRouter(tags=["executed-sets"])


@router.post("/sessions/{session_id}/units/{unit_id}/sets", response_model=SessionResponse, response_model_by_alias=True, status_code=201)
async def add_set(
    session_id: str, unit_id: str, body: ExecutedSetCreate, current_user: User = Depends(get_current_user)
):
    session = await get_user_session(session_id, current_user)
    unit = next((u for u in session.workout_units if str(u.id) == unit_id), None)
    if unit is None:
        raise_not_found("WorkoutUnit")

    exercise = await Exercise.get(PydanticObjectId(body.exercise_id), fetch_links=True)
    if exercise is None:
        raise_not_found("Exercise")

    new_set = ExecutedSet(
        exercise=exercise,
        load=body.load,
        load_description=body.load_description,
        repetitions=body.repetitions,
        notes=body.notes,
    )
    unit.executed_sets.append(new_set)
    session.updated_at = datetime.utcnow()
    await session.save()
    logger.info(f"ExecutedSet {new_set.id} added to WorkoutUnit {unit_id}")
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)


@router.put("/sessions/{session_id}/units/{unit_id}/sets/{set_id}", response_model=SessionResponse, response_model_by_alias=True)
async def update_set(
    session_id: str,
    unit_id: str,
    set_id: str,
    body: ExecutedSetUpdate,
    current_user: User = Depends(get_current_user),
):
    session = await get_user_session(session_id, current_user)
    unit = next((u for u in session.workout_units if str(u.id) == unit_id), None)
    if unit is None:
        raise_not_found("WorkoutUnit")
    es = next((s for s in unit.executed_sets if str(s.id) == set_id), None)
    if es is None:
        raise_not_found("ExecutedSet")

    if body.load is not None:
        es.load = body.load
    if body.load_description is not None:
        es.load_description = body.load_description
    if body.repetitions is not None:
        es.repetitions = body.repetitions
    if body.notes is not None:
        es.notes = body.notes
    if body.exercise_id is not None:
        exercise = await Exercise.get(PydanticObjectId(body.exercise_id), fetch_links=True)
        if exercise is None:
            raise_not_found("Exercise")
        es.exercise = exercise

    session.updated_at = datetime.utcnow()
    await session.save()
    logger.info(f"ExecutedSet {set_id} updated in WorkoutUnit {unit_id}")
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)


@router.delete("/sessions/{session_id}/units/{unit_id}/sets/{set_id}", status_code=204)
async def delete_set(
    session_id: str, unit_id: str, set_id: str, current_user: User = Depends(get_current_user)
):
    session = await get_user_session(session_id, current_user)
    unit = next((u for u in session.workout_units if str(u.id) == unit_id), None)
    if unit is None:
        raise_not_found("WorkoutUnit")
    original_len = len(unit.executed_sets)
    unit.executed_sets = [s for s in unit.executed_sets if str(s.id) != set_id]
    if len(unit.executed_sets) == original_len:
        raise HTTPException(status_code=404, detail="ExecutedSet not found.")
    session.updated_at = datetime.utcnow()
    await session.save()
    logger.info(f"ExecutedSet {set_id} deleted from WorkoutUnit {unit_id}")


@router.patch("/sessions/{session_id}/units/{unit_id}/sets/reorder", response_model=SessionResponse, response_model_by_alias=True)
async def reorder_sets(
    session_id: str,
    unit_id: str,
    body: ReorderRequest,
    current_user: User = Depends(get_current_user),
):
    session = await get_user_session(session_id, current_user)
    unit = next((u for u in session.workout_units if str(u.id) == unit_id), None)
    if unit is None:
        raise_not_found("WorkoutUnit")
    set_map = {str(s.id): s for s in unit.executed_sets}
    unit.executed_sets = [set_map[id] for id in body.ordered_ids if id in set_map]
    session.updated_at = datetime.utcnow()
    await session.save()
    session = await Session.get(session.id, fetch_links=True)
    return to_session_response(session)
