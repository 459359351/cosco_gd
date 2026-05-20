from pydantic import BaseModel


class AlertItem(BaseModel):
    id: int
    yard_id: int
    level: str
    alert_type: str
    message: str
    created_at: str


class AlertList(BaseModel):
    items: list[AlertItem]
