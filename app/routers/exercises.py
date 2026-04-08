import logging
from beanie import PydanticObjectId
from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.models.exercise import Exercise
from app.models.muscle_group import MuscleGroup
from app.models.session import Session
from app.models.training_type import TrainingType
from app.models.user import User
from app.schemas.exercise import ExerciseCreate, ExerciseResponse, ExerciseUpdate
from app.schemas.muscle_group import MuscleGroupResponse
from app.schemas.training_type import TrainingTypeResponse

logger = logging.getLogger("mytraining")
router = APIRouter(prefix="/exercises", tags=["exercises"])


def to_response(ex: Exercise) -> ExerciseResponse:
    tt: TrainingType = ex.training_type  # type: ignore[assignment]
    mg: MuscleGroup = ex.muscle_group  # type: ignore[assignment]
    return ExerciseResponse(
        id=str(ex.id),
        name=ex.name,
        training_type=TrainingTypeResponse(id=str(tt.id), name=tt.name, description=tt.description),
        muscle_group=MuscleGroupResponse(id=str(mg.id), name=mg.name, description=mg.description),
        execution_description=ex.execution_description,
        load_description=ex.load_description,
        notes=ex.notes,
    )


@router.get("", response_model=list[ExerciseResponse])
async def list_exercises(
    trainingTypeId: str | None = None,
    muscleGroupId: str | None = None,
    _: User = Depends(get_current_user),
):
    query: dict = {}
    if trainingTypeId:
        query["training_type.$id"] = PydanticObjectId(trainingTypeId)
    if muscleGroupId:
        query["muscle_group.$id"] = PydanticObjectId(muscleGroupId)
    items = await Exercise.find(query, fetch_links=True).to_list()
    return [to_response(ex) for ex in items]


@router.get("/{id}", response_model=ExerciseResponse)
async def get_exercise(id: str, _: User = Depends(get_current_user)):
    ex = await Exercise.get(PydanticObjectId(id), fetch_links=True)
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found.")
    return to_response(ex)


@router.post("", response_model=ExerciseResponse, status_code=201)
async def create_exercise(body: ExerciseCreate, _: User = Depends(get_current_user)):
    tt = await TrainingType.get(PydanticObjectId(body.training_type_id))
    if tt is None:
        raise HTTPException(status_code=404, detail="TrainingType not found.")
    mg = await MuscleGroup.get(PydanticObjectId(body.muscle_group_id))
    if mg is None:
        raise HTTPException(status_code=404, detail="MuscleGroup not found.")

    ex = Exercise(
        name=body.name,
        training_type=tt,
        muscle_group=mg,
        execution_description=body.execution_description,
        load_description=body.load_description,
        notes=body.notes,
    )
    await ex.insert()
    logger.info(f"Exercise {ex.id} created")
    ex = await Exercise.get(ex.id, fetch_links=True)
    return to_response(ex)


@router.put("/{id}", response_model=ExerciseResponse)
async def update_exercise(id: str, body: ExerciseUpdate, _: User = Depends(get_current_user)):
    ex = await Exercise.get(PydanticObjectId(id))
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    if body.name is not None:
        ex.name = body.name
    if body.execution_description is not None:
        ex.execution_description = body.execution_description
    if body.load_description is not None:
        ex.load_description = body.load_description
    if body.notes is not None:
        ex.notes = body.notes
    if body.training_type_id is not None:
        tt = await TrainingType.get(PydanticObjectId(body.training_type_id))
        if tt is None:
            raise HTTPException(status_code=404, detail="TrainingType not found.")
        ex.training_type = tt
    if body.muscle_group_id is not None:
        mg = await MuscleGroup.get(PydanticObjectId(body.muscle_group_id))
        if mg is None:
            raise HTTPException(status_code=404, detail="MuscleGroup not found.")
        ex.muscle_group = mg

    await ex.save()
    logger.info(f"Exercise {id} updated")
    ex = await Exercise.get(ex.id, fetch_links=True)
    return to_response(ex)


@router.delete("/{id}", status_code=204)
async def delete_exercise(id: str, _: User = Depends(get_current_user)):
    ex = await Exercise.get(PydanticObjectId(id))
    if ex is None:
        raise HTTPException(status_code=404, detail="Exercise not found.")

    ref_sets = await Session.find({"workout_units.executed_sets.exercise.$id": PydanticObjectId(id)}).count()
    if ref_sets > 0:
        logger.warning(f"Delete blocked: Exercise {id} referenced by {ref_sets} session(s)")
        raise HTTPException(status_code=409, detail=f"Exercise is referenced by {ref_sets} session(s) and cannot be deleted.")

    await ex.delete()
    logger.info(f"Exercise {id} deleted")
