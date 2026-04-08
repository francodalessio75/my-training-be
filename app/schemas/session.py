from datetime import datetime
from pydantic import BaseModel
from app.schemas.workout_unit import WorkoutUnitResponse, WorkoutUnitSummaryResponse


class SessionCreate(BaseModel):
    name: str
    date: datetime
    total_load_description: str
    notes: str | None = None


class SessionUpdate(BaseModel):
    name: str | None = None
    date: datetime | None = None
    total_load_description: str | None = None
    notes: str | None = None


class SessionResponse(BaseModel):
    id: str
    user_id: str
    name: str
    date: datetime
    workout_units: list[WorkoutUnitResponse]
    total_load_description: str
    notes: str | None = None
    created_at: datetime
    updated_at: datetime


class SessionListItemResponse(BaseModel):
    id: str
    name: str
    date: datetime
    workout_units: list[WorkoutUnitSummaryResponse]
    total_load_description: str
