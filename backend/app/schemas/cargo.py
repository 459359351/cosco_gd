from pydantic import BaseModel


class CargoItem(BaseModel):
    category: str
    volume: int


class CargoDistribution(BaseModel):
    items: list[CargoItem]
