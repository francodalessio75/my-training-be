import logging
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.session import Session
from app.models.training_type import TrainingType
from app.models.user import User
from app.schemas.training_type import TrainingTypeCreate, TrainingTypeResponse, TrainingTypeUpdate

logger = logging.getLogger("mytraining")
router = APIRouter(prefix="/training-types", tags=["training-types"])


def to_response(tt: TrainingType) -> TrainingTypeResponse:
    return TrainingTypeResponse(id=str(tt.id), name=tt.name, description=tt.description)


@router.get("", response_model=list[TrainingTypeResponse])
async def list_training_types(_: User = Depends(get_current_user)):
    return [to_response(tt) for tt in await TrainingType.find_all().to_list()]


@router.post("", response_model=TrainingTypeResponse, status_code=201)
async def create_training_type(body: TrainingTypeCreate, _: User = Depends(get_current_user)):
    tt = TrainingType(**body.model_dump())
    await tt.insert()
    logger.info(f"TrainingType {tt.id} created")
    return to_response(tt)


@router.put("/{id}", response_model=TrainingTypeResponse)
async def update_training_type(id: str, body: TrainingTypeUpdate, _: User = Depends(get_current_user)):
    tt = await TrainingType.get(PydanticObjectId(id))
    if tt is None:
        raise HTTPException(status_code=404, detail="TrainingType not found.")
    update_data = body.model_dump(exclude_none=True)
    if update_data:
        await tt.set(update_data)
    logger.info(f"TrainingType {id} updated")
    return to_response(tt)


@router.delete("/{id}", status_code=204)
async def delete_training_type(id: str, _: User = Depends(get_current_user)):
    tt = await TrainingType.get(PydanticObjectId(id))
    if tt is None:
        raise HTTPException(status_code=404, detail="TrainingType not found.")

    ref_exercises = await Exercise.find({"training_type.$id": PydanticObjectId(id)}).count()
    ref_sessions = await Session.find({"workout_units.training_type.$id": PydanticObjectId(id)}).count()
    total = ref_exercises + ref_sessions
    if total > 0:
        logger.warning(f"Delete blocked: TrainingType {id} referenced by {total} document(s)")
        raise HTTPException(status_code=409, detail=f"TrainingType is referenced by {total} document(s) and cannot be deleted.")

    await tt.delete()
    logger.info(f"TrainingType {id} deleted")
