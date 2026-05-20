from pydantic import BaseModel


class FlowItem(BaseModel):
    from_code: str
    to_code: str
    value: int


class FlowOD(BaseModel):
    items: list[FlowItem]
