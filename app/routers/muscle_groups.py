import logging
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.muscle_group import MuscleGroup
from app.models.user import User
from app.schemas.common import raise_not_found
from app.schemas.muscle_group import MuscleGroupCreate, MuscleGroupResponse, MuscleGroupUpdate

logger = logging.getLogger("mytraining")
router = APIRouter(prefix="/muscle-groups", tags=["muscle-groups"])


def to_response(mg: MuscleGroup) -> MuscleGroupResponse:
    return MuscleGroupResponse(id=str(mg.id), name=mg.name, description=mg.description)


@router.get("", response_model=list[MuscleGroupResponse], response_model_by_alias=True)
async def list_muscle_groups(_: User = Depends(get_current_user)):
    return [to_response(mg) for mg in await MuscleGroup.find_all().to_list()]


@router.post("", response_model=MuscleGroupResponse, response_model_by_alias=True, status_code=201)
async def create_muscle_group(body: MuscleGroupCreate, _: User = Depends(get_current_user)):
    mg = MuscleGroup(**body.model_dump())
    await mg.insert()
    logger.info(f"MuscleGroup {mg.id} created")
    return to_response(mg)


@router.put("/{id}", response_model=MuscleGroupResponse, response_model_by_alias=True)
async def update_muscle_group(id: str, body: MuscleGroupUpdate, _: User = Depends(get_current_user)):
    mg = await MuscleGroup.get(PydanticObjectId(id))
    if mg is None:
        raise_not_found("MuscleGroup")
    update_data = body.model_dump(exclude_none=True)
    if update_data:
        await mg.set(update_data)
    logger.info(f"MuscleGroup {id} updated")
    return to_response(mg)


@router.delete("/{id}", status_code=204)
async def delete_muscle_group(id: str, _: User = Depends(get_current_user)):
    mg = await MuscleGroup.get(PydanticObjectId(id))
    if mg is None:
        raise_not_found("MuscleGroup")

    ref_exercises = await Exercise.find({"muscle_group.$id": PydanticObjectId(id)}).count()
    if ref_exercises > 0:
        logger.warning(f"Delete blocked: MuscleGroup {id} referenced by {ref_exercises} exercise(s)")
        raise HTTPException(status_code=409, detail=f"MuscleGroup is referenced by {ref_exercises} exercise(s) and cannot be deleted.")

    await mg.delete()
    logger.info(f"MuscleGroup {id} deleted")
