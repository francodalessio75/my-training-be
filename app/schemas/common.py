from pydantic import BaseModel


class ReorderRequest(BaseModel):
    ordered_ids: list[str]
