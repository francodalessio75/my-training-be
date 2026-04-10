from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class ReorderRequest(CamelModel):
    ordered_ids: list[str]


def raise_not_found(resource: str = "Resource"):
    raise HTTPException(status_code=404, detail=f"{resource} not found.")
