from pydantic import BaseModel


class TrendPoint(BaseModel):
    date: str
    in_teu: int
    out_teu: int
    stock_teu: int


class ThroughputTrend(BaseModel):
    points: list[TrendPoint]
