from pydantic import BaseModel


class MuscleGroupCreate(BaseModel):
    name: str
    description: str | None = None


class MuscleGroupUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class MuscleGroupResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
