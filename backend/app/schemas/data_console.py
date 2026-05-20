from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

# —— 堆场 ——


class YardRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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


class YardCreate(BaseModel):
    name: str = Field(..., max_length=120)
    code: str = Field(..., max_length=60)
    yard_type: str = Field(default="yard", max_length=40)
    province: str = Field(..., max_length=40)
    city: str = Field(..., max_length=40)
    lng: float
    lat: float
    capacity: int = 0
    status: str = Field(default="normal", max_length=20)


class YardUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=120)
    yard_type: str | None = Field(default=None, max_length=40)
    province: str | None = Field(default=None, max_length=40)
    city: str | None = Field(default=None, max_length=40)
    lng: float | None = None
    lat: float | None = None
    capacity: int | None = None
    status: str | None = Field(default=None, max_length=20)


# —— OD 飞线 ——


class FlowODRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    from_yard_code: str
    to_yard_code: str
    value_teu: int


class FlowODCreate(BaseModel):
    from_yard_code: str = Field(..., max_length=60)
    to_yard_code: str = Field(..., max_length=60)
    value_teu: int = 0


class FlowODUpdate(BaseModel):
    from_yard_code: str | None = Field(default=None, max_length=60)
    to_yard_code: str | None = Field(default=None, max_length=60)
    value_teu: int | None = None


# —— 日吞吐 ——


class ThroughputRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    yard_id: int
    stat_date: date
    in_teu: int
    out_teu: int
    stock_teu: int


class ThroughputCreate(BaseModel):
    yard_id: int
    stat_date: date
    in_teu: int = 0
    out_teu: int = 0
    stock_teu: int = 0


class ThroughputUpdate(BaseModel):
    in_teu: int | None = None
    out_teu: int | None = None
    stock_teu: int | None = None


# —— 货种 ——


class CargoRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    yard_id: int
    category: str
    volume: int


class CargoCreate(BaseModel):
    yard_id: int
    category: str = Field(..., max_length=50)
    volume: int = 0


class CargoUpdate(BaseModel):
    category: str | None = Field(default=None, max_length=50)
    volume: int | None = None


# —— 预警 ——


class AlertRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    yard_id: int
    level: str
    alert_type: str
    message: str
    created_at: datetime


class AlertCreate(BaseModel):
    yard_id: int
    level: str = Field(default="info", max_length=20)
    alert_type: str = Field(..., max_length=40)
    message: str


class AlertUpdate(BaseModel):
    level: str | None = Field(default=None, max_length=20)
    alert_type: str | None = Field(default=None, max_length=40)
    message: str | None = None


# —— 车辆 ——


class VehicleRowOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    from_yard_code: str
    to_yard_code: str
    progress: float
    status: str


class VehicleCreate(BaseModel):
    code: str = Field(..., max_length=50)
    from_yard_code: str = Field(..., max_length=60)
    to_yard_code: str = Field(..., max_length=60)
    progress: float = 0.0
    status: str = Field(default="running", max_length=20)


class VehicleUpdate(BaseModel):
    from_yard_code: str | None = Field(default=None, max_length=60)
    to_yard_code: str | None = Field(default=None, max_length=60)
    progress: float | None = None
    status: str | None = Field(default=None, max_length=20)


class ImportResult(BaseModel):
    inserted: int = 0
    updated: int = 0
    errors: list[dict] = []
