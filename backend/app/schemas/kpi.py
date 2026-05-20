from pydantic import BaseModel


class KpiOverview(BaseModel):
    yard_count: int
    total_stock_teu: int
    today_throughput: int
    in_transit_vehicles: int
