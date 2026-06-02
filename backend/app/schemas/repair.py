from pydantic import BaseModel


class RepairKpiBlock(BaseModel):
    container_qty: int = 0
    qty_wow: float = 0.0
    revenue: float = 0.0
    rev_wow: float = 0.0
    unit_price: float = 0.0
    qty_yoy: int | None = None
    rev_yoy: float | None = None


class RepairKpiOverview(BaseModel):
    self_: RepairKpiBlock = RepairKpiBlock()
    outsourced: RepairKpiBlock = RepairKpiBlock()
    thirdparty: RepairKpiBlock = RepairKpiBlock()
    cosco: RepairKpiBlock = RepairKpiBlock()
    total: RepairKpiBlock = RepairKpiBlock()
    week_label: str = ""


class OrgRankItem(BaseModel):
    org_name: str
    org_code: str
    company_type: str
    container_qty: int = 0
    revenue: float = 0.0
    qty_wow: float = 0.0
    rev_wow: float = 0.0
    total_qty: int = 0
    total_revenue: float = 0.0


class SiteDrilldownItem(BaseModel):
    site_name: str
    repair_qty: int = 0
    approved_amount: float = 0.0
    customer_names: list[str] = []
    pct: float = 0.0


class SiteDrilldownResponse(BaseModel):
    parent_name: str
    company_type: str
    items: list[SiteDrilldownItem] = []


class CustomerDistItem(BaseModel):
    customer_type: str
    container_qty: int = 0
    revenue: float = 0.0
    pct_qty: float = 0.0
    pct_rev: float = 0.0


class CumulativeItem(BaseModel):
    org_name: str
    cum_qty: int = 0
    cum_qty_yoy: int = 0
    cum_revenue: float = 0.0
    cum_revenue_yoy: float = 0.0


class NetworkSiteItem(BaseModel):
    name: str
    code: str
    company_type: str
    parent_name: str = ""
    province: str = ""
    city: str = ""
    lng: float = 0.0
    lat: float = 0.0
    status: str = ""
