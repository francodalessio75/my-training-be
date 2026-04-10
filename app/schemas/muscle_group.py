from app.schemas.common import CamelModel


class MuscleGroupCreate(CamelModel):
    name: str
    description: str | None = None


class MuscleGroupUpdate(CamelModel):
    name: str | None = None
    description: str | None = None


class MuscleGroupResponse(CamelModel):
    id: str
    name: str
    description: str | None = None
