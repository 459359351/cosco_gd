from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.repair import (
    RepairNetworkSite,
    RepairWeeklyCumulative,
    RepairWeeklyOrg,
    RepairWeeklySiteDetail,
    RepairWeeklySummary,
)
from app.schemas.repair import (
    CumulativeItem,
    CustomerDistItem,
    NetworkSiteItem,
    OrgRankItem,
    RepairKpiBlock,
    RepairKpiOverview,
    SiteDrilldownItem,
    SiteDrilldownResponse,
)

router = APIRouter(tags=["repair"])


@router.get("/network-sites")
async def get_network_sites(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(RepairNetworkSite))).scalars().all()
    return [
        {
            "name": r.name,
            "code": r.code,
            "company_type": r.company_type,
            "parent_name": r.parent_name,
            "province": r.province,
            "city": r.city,
            "lng": r.lng,
            "lat": r.lat,
            "distance": r.distance or 0,
            "status": r.status,
        }
        for r in rows
    ]


@router.post("/network-sites/geocode")
async def geocode_network_sites(
    items: list[dict] = Body(..., description="[{code, lng, lat, province?, city?}]"),
    db: AsyncSession = Depends(get_db),
):
    """前端批量解析坐标后回写。"""
    if not items:
        return {"updated": 0}

    updated = 0
    for item in items:
        code = item.get("code")
        if not code:
            continue
        row = (await db.execute(
            select(RepairNetworkSite).where(RepairNetworkSite.code == code)
        )).scalar_one_or_none()
        if row:
            row.lng = item.get("lng", 0.0)
            row.lat = item.get("lat", 0.0)
            row.province = item.get("province", "")
            row.city = item.get("city", "")
            updated += 1

    await db.commit()
    return {"updated": updated}


@router.get("/kpi", response_model=RepairKpiOverview)
async def get_repair_kpi(
    year: int = Query(2026),
    week: int = Query(20),
    db: AsyncSession = Depends(get_db),
):
    result = RepairKpiOverview(week_label=f"{year}年第{week}周")

    rows = (await db.execute(
        select(RepairWeeklySummary).where(
            RepairWeeklySummary.year == year,
            RepairWeeklySummary.week == week,
        )
    )).scalars().all()

    if not rows:
        return result

    summary_map: dict[str, dict[str, RepairWeeklySummary]] = {}
    for r in rows:
        summary_map.setdefault(r.summary_type, {})[r.customer_type] = r

    def _build_block(stype: str) -> RepairKpiBlock:
        cosco = summary_map.get(stype, {}).get("cosco")
        tp = summary_map.get(stype, {}).get("thirdparty")
        if not cosco:
            return RepairKpiBlock()
        return RepairKpiBlock(
            container_qty=cosco.container_qty,
            qty_wow=cosco.qty_wow_change,
            revenue=cosco.revenue,
            rev_wow=cosco.rev_wow_change,
        )

    result.self_ = _build_block("self_total")
    result.outsourced = _build_block("outsourced_total")

    # combined_total: cosco = 全部中远海, thirdparty = 全部第三方
    combined_cosco = summary_map.get("combined_total", {}).get("cosco")
    combined_third = summary_map.get("combined_total", {}).get("thirdparty")

    if combined_cosco:
        result.cosco = RepairKpiBlock(
            container_qty=combined_cosco.container_qty,
            qty_wow=combined_cosco.qty_wow_change,
            revenue=combined_cosco.revenue,
            rev_wow=combined_cosco.rev_wow_change,
            unit_price=combined_cosco.unit_price,
        )

    if combined_third:
        result.thirdparty = RepairKpiBlock(
            container_qty=combined_third.container_qty,
            qty_wow=combined_third.qty_wow_change,
            revenue=combined_third.revenue,
            rev_wow=combined_third.rev_wow_change,
            unit_price=combined_third.unit_price,
        )

    if combined_cosco and combined_third:
        total_qty = combined_cosco.container_qty + combined_third.container_qty
        total_rev = combined_cosco.revenue + combined_third.revenue
        result.total = RepairKpiBlock(
            container_qty=total_qty,
            qty_wow=combined_cosco.qty_wow_change + combined_third.qty_wow_change,
            revenue=total_rev,
            rev_wow=combined_cosco.rev_wow_change + combined_third.rev_wow_change,
            unit_price=round(total_rev / total_qty, 2) if total_qty else 0,
        )

    # 同比: 查找 2025 年第 19 周数据
    prev_year, prev_week = _get_yoy_year_week(year, week)
    prev_rows = (await db.execute(
        select(RepairWeeklySummary).where(
            RepairWeeklySummary.year == prev_year,
            RepairWeeklySummary.week == prev_week,
        )
    )).scalars().all()

    if prev_rows:
        prev_map: dict[str, dict[str, RepairWeeklySummary]] = {}
        for r in prev_rows:
            prev_map.setdefault(r.summary_type, {})[r.customer_type] = r

        for attr, stype in [("self_", "self_total"), ("outsourced", "outsourced_total")]:
            curr = summary_map.get(stype, {}).get("cosco")
            prev = prev_map.get(stype, {}).get("cosco")
            if curr and prev:
                block = getattr(result, attr)
                block.qty_yoy = curr.container_qty - prev.container_qty
                block.rev_yoy = curr.revenue - prev.revenue

    return result


@router.get("/org-ranking", response_model=list[OrgRankItem])
async def get_repair_org_ranking(
    company_type: str = Query("self"),
    metric: str = Query("revenue"),
    top: int = Query(10),
    year: int = Query(2026),
    week: int = Query(20),
    db: AsyncSession = Depends(get_db),
):
    col = RepairWeeklyOrg.revenue if metric == "revenue" else RepairWeeklyOrg.container_qty
    stmt = (
        select(RepairWeeklyOrg)
        .where(
            RepairWeeklyOrg.year == year,
            RepairWeeklyOrg.week == week,
            RepairWeeklyOrg.company_type == company_type,
            RepairWeeklyOrg.customer_type == "cosco",
        )
        .order_by(col.desc())
        .limit(top)
    )
    rows = (await db.execute(stmt)).scalars().all()

    items = []
    for r in rows:
        items.append(OrgRankItem(
            org_name=r.org_name,
            org_code=r.org_code,
            company_type=r.company_type,
            container_qty=r.container_qty,
            revenue=r.revenue,
            qty_wow=r.qty_wow_change,
            rev_wow=r.rev_wow_change,
            total_qty=r.total_qty,
            total_revenue=r.total_revenue,
        ))
    return items


@router.get("/site-drilldown", response_model=SiteDrilldownResponse)
async def get_repair_site_drilldown(
    parent_name: str = Query(...),
    year: int = Query(2026),
    week: int = Query(20),
    db: AsyncSession = Depends(get_db),
):
    # 先获取该父机构下属的所有网点名
    child_sites = (await db.execute(
        select(RepairNetworkSite.name, RepairNetworkSite.company_type).where(
            RepairNetworkSite.parent_name == parent_name
        )
    )).all()
    child_names = {r[0] for r in child_sites}
    parent_type = child_sites[0][1] if child_sites else ""

    rows = (await db.execute(
        select(RepairWeeklySiteDetail)
        .where(
            RepairWeeklySiteDetail.year == year,
            RepairWeeklySiteDetail.week == week,
        )
    )).scalars().all()

    site_agg: dict[str, dict] = {}
    for r in rows:
        if r.site_name not in child_names:
            continue
        if r.site_name not in site_agg:
            site_agg[r.site_name] = {"repair_qty": 0, "approved_amount": 0.0, "customers": set()}
        site_agg[r.site_name]["repair_qty"] += r.repair_qty
        site_agg[r.site_name]["approved_amount"] += r.approved_amount
        if r.customer_name:
            site_agg[r.site_name]["customers"].add(r.customer_name)

    total_amount = sum(v["approved_amount"] for v in site_agg.values()) or 1

    items = sorted(site_agg.items(), key=lambda x: x[1]["approved_amount"], reverse=True)
    return SiteDrilldownResponse(
        parent_name=parent_name,
        company_type=parent_type,
        items=[
            SiteDrilldownItem(
                site_name=name,
                repair_qty=val["repair_qty"],
                approved_amount=round(val["approved_amount"], 2),
                customer_names=sorted(val["customers"]),
                pct=round(val["approved_amount"] / total_amount * 100, 1),
            )
            for name, val in items
        ],
    )


@router.get("/customer-dist", response_model=list[CustomerDistItem])
async def get_repair_customer_dist(
    year: int = Query(2026),
    week: int = Query(20),
    db: AsyncSession = Depends(get_db),
):
    rows = (await db.execute(
        select(RepairWeeklySummary).where(
            RepairWeeklySummary.year == year,
            RepairWeeklySummary.week == week,
            RepairWeeklySummary.summary_type == "combined_total",
        )
    )).scalars().all()

    if not rows:
        return []

    total_qty = sum(r.container_qty for r in rows) or 1
    total_rev = sum(r.revenue for r in rows) or 1

    result = []
    for r in rows:
        result.append(CustomerDistItem(
            customer_type=r.customer_type,
            container_qty=r.container_qty,
            revenue=round(r.revenue, 2),
            pct_qty=round(r.container_qty / total_qty * 100, 1),
            pct_rev=round(r.revenue / total_rev * 100, 1),
        ))
    return result


@router.get("/cumulative", response_model=list[CumulativeItem])
async def get_repair_cumulative(
    year: int = Query(2026),
    week: int = Query(20),
    db: AsyncSession = Depends(get_db),
):
    rows = (await db.execute(
        select(RepairWeeklyCumulative).where(
            RepairWeeklyCumulative.year == year,
            RepairWeeklyCumulative.week == week,
        ).order_by(RepairWeeklyCumulative.cum_qty.desc())
    )).scalars().all()

    return [
        CumulativeItem(
            org_name=r.org_name,
            cum_qty=r.cum_qty,
            cum_qty_yoy=r.cum_qty_yoy,
            cum_revenue=r.cum_revenue,
            cum_revenue_yoy=r.cum_revenue_yoy,
        )
        for r in rows
    ]


def _get_yoy_year_week(year: int, week: int) -> tuple[int, int]:
    """同比对照：2026第20周 → 2025第19周（业务确认的偏移）。"""
    return year - 1, week - 1
