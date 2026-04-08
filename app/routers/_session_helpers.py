from beanie import PydanticObjectId
from fastapi import HTTPException
from app.models.exercise import Exercise
from app.models.muscle_group import MuscleGroup
from app.models.session import ExecutedSet, Session, WorkoutUnit
from app.models.training_type import TrainingType
from app.models.user import User
from app.schemas.executed_set import ExecutedSetResponse
from app.schemas.exercise import ExerciseResponse
from app.schemas.muscle_group import MuscleGroupResponse
from app.schemas.session import SessionListItemResponse, SessionResponse
from app.schemas.training_type import TrainingTypeResponse
from app.schemas.workout_unit import WorkoutUnitResponse, WorkoutUnitSummaryResponse


def _tt_response(tt: TrainingType) -> TrainingTypeResponse:
    return TrainingTypeResponse(id=str(tt.id), name=tt.name, description=tt.description)


def _mg_response(mg: MuscleGroup) -> MuscleGroupResponse:
    return MuscleGroupResponse(id=str(mg.id), name=mg.name, description=mg.description)


def _ex_response(ex: Exercise) -> ExerciseResponse:
    return ExerciseResponse(
        id=str(ex.id),
        name=ex.name,
        training_type=_tt_response(ex.training_type),  # type: ignore[arg-type]
        muscle_group=_mg_response(ex.muscle_group),  # type: ignore[arg-type]
        execution_description=ex.execution_description,
        load_description=ex.load_description,
        notes=ex.notes,
    )


def _set_response(s: ExecutedSet) -> ExecutedSetResponse:
    return ExecutedSetResponse(
        id=str(s.id),
        exercise=_ex_response(s.exercise),  # type: ignore[arg-type]
        load=s.load,
        load_description=s.load_description,
        repetitions=s.repetitions,
        notes=s.notes,
    )


def _unit_response(wu: WorkoutUnit) -> WorkoutUnitResponse:
    return WorkoutUnitResponse(
        id=str(wu.id),
        training_type=_tt_response(wu.training_type),  # type: ignore[arg-type]
        executed_sets=[_set_response(s) for s in wu.executed_sets],
        total_load_description=wu.total_load_description,
        notes=wu.notes,
    )


def to_session_response(session: Session) -> SessionResponse:
    return SessionResponse(
        id=str(session.id),
        user_id=session.user_id,
        name=session.name,
        date=session.date,
        workout_units=[_unit_response(wu) for wu in session.workout_units],
        total_load_description=session.total_load_description,
        notes=session.notes,
        created_at=session.created_at,
        updated_at=session.updated_at,
    )


def to_session_list_response(session: Session) -> SessionListItemResponse:
    return SessionListItemResponse(
        id=str(session.id),
        name=session.name,
        date=session.date,
        workout_units=[
            WorkoutUnitSummaryResponse(
                id=str(wu.id),
                training_type=_tt_response(wu.training_type),  # type: ignore[arg-type]
            )
            for wu in session.workout_units
        ],
        total_load_description=session.total_load_description,
    )


async def get_user_session(session_id: str, current_user: User) -> Session:
    session = await Session.get(PydanticObjectId(session_id))
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    if session.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Forbidden.")
    return session
