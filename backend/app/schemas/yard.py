from pydantic import BaseModel


class YardBase(BaseModel):
    id: int
    name: str
    code: str
    yard_type: str
    province: str
    city: str
    lng: float
    lat: float
    capacity: int
    status: str


class YardGeoFeature(BaseModel):
    type: str = "Feature"
    properties: YardBase
    geometry: dict


class YardDetail(BaseModel):
    yard: YardBase
    today_in_teu: int
    today_out_teu: int
    stock_teu: int
