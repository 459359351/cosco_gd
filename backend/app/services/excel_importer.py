"""Excel 周报导入解析器 — 基于内容识别区域，不硬编码行号。"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from openpyxl import load_workbook
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.repair import (
    ExcelUploadLog,
    RepairNetworkSite,
    RepairWeeklyCumulative,
    RepairWeeklyOrg,
    RepairWeeklySiteDetail,
    RepairWeeklySummary,
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

SELF_ORG_NAMES = {
    "深圳运营中心",
    "广州运营中心",
    "珠三角运营中心",
    "粤西运营中心",
    "北部湾运营中心",
    "南岗分公司",
}

TOTAL_PATTERNS = {
    "combined_total": ("自营外包总计",),
    "self_total": ("自营总计",),
    "outsourced_total": ("外包总计",),
}

YOY_ROLE_KEYWORDS = {
    "inspection": ("检修",),
    "network": ("经营单位",),
    "cumulative": ("周完成", "完成情况"),
}


def _safe_float(val) -> float:
    if val is None:
        return 0.0
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _safe_int(val) -> int:
    if val is None:
        return 0
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0


def _cell(ws, row: int, col: int):
    v = ws.cell(row=row, column=col).value
    return None if v is None or (isinstance(v, str) and v.strip() == "") else v


def _classify_company(name: str) -> str:
    """判断经营单位是自营还是外包。"""
    return "self" if name in SELF_ORG_NAMES else "outsourced"


def _make_code(name: str) -> str:
    return re.sub(r"[^\w一-鿿]", "", name)


_SHEET_WEEK_RE = re.compile(r"(\d{4})\s*年?\s*第?\s*(\d{1,2})\s*周")


def parse_sheet_name(name: str) -> dict:
    m = _SHEET_WEEK_RE.search(name)
    info: dict = {"detected_year": None, "detected_week": None, "suggested_role": None}
    if m:
        info["detected_year"] = int(m.group(1))
        info["detected_week"] = int(m.group(2))
    for role, keywords in YOY_ROLE_KEYWORDS.items():
        if any(k in name for k in keywords):
            info["suggested_role"] = role
            break
    return info


# ---------------------------------------------------------------------------
# 主解析器
# ---------------------------------------------------------------------------


class WeeklyExcelImporter:
    def __init__(self, file_path: str | Path, year: int, week: int):
        self.file_path = Path(file_path)
        self.year = year
        self.week = week
        self.wb = load_workbook(str(self.file_path), data_only=True)
        self.row_counts: dict[str, int] = {}
        self.site_registry: dict[str, dict] = {}

    # -- 公共入口 --

    def parse_all(self) -> dict:
        return {
            "orgs": self._parse_main_sheet(),
            "summaries": self._parse_main_sheet_summaries(),
            "site_details": self._parse_inspection_sheet(),
            "sites": self._parse_network_sites_sheet(),
            "cumulative": self._parse_cumulative_sheet(),
        }

    def parse_yoy(self, yoy_sheet_name: str) -> dict:
        prev_year, prev_week = self._get_yoy_year_week()
        if yoy_sheet_name not in self.wb.sheetnames:
            return {"yoy_orgs": [], "yoy_summaries": []}
        ws = self.wb[yoy_sheet_name]
        return {
            "yoy_orgs": self._parse_org_rows(ws, prev_year, prev_week),
            "yoy_summaries": self._parse_summary_rows(ws, prev_year, prev_week),
        }

    def preview_sheets(self) -> list[dict]:
        sheets: list[dict] = []
        prev_year, prev_week = self._get_yoy_year_week()
        for name in self.wb.sheetnames:
            info = parse_sheet_name(name)
            if info["detected_year"] == self.year and info["detected_week"] == self.week:
                info["suggested_role"] = "current"
            elif info["detected_year"] == prev_year and info["detected_week"] == prev_week:
                info["suggested_role"] = "yoy"
            elif info["suggested_role"] is None:
                info["suggested_role"] = None
            sheets.append({"name": name, **info})
        return sheets

    # -- Sheet 定位 --

    def _find_sheet(self, *keywords: str):
        for name in self.wb.sheetnames:
            if all(k in name for k in keywords):
                return self.wb[name]
        return None

    def _find_main_sheet(self):
        """根据 year/week 定位主数据 Sheet。"""
        target_year = str(self.year)
        week_str = str(self.week)
        for name in self.wb.sheetnames:
            if target_year in name and (f"第{week_str}周" in name or f"{week_str}周" in name):
                if "新" not in name and "洗" not in name and "纯" not in name:
                    return self.wb[name]
        return None

    # -- 解析主 Sheet 机构行 --

    def _parse_main_sheet(self) -> list[dict]:
        ws = self._find_main_sheet()
        if ws is None:
            return []
        records = self._parse_org_rows(ws, self.year, self.week)
        self.row_counts["orgs"] = len(records)
        return records

    def _parse_org_rows(self, ws, target_year: int, target_week: int) -> list[dict]:
        records: list[dict] = []
        current_type = ""
        in_summary_zone = False

        for row_idx in range(4, ws.max_row + 1):
            a_val = _cell(ws, row_idx, 1)
            b_val = _cell(ws, row_idx, 2)

            if a_val and "网点明细" in str(a_val):
                break
            if a_val and "全部干箱" in str(a_val):
                in_summary_zone = True
            if in_summary_zone:
                continue

            if a_val and "自营" in str(a_val) and "合作" not in str(a_val) and "外包" not in str(a_val):
                current_type = "self"
            elif a_val and "合作供应商" in str(a_val):
                current_type = "outsourced"

            if not b_val:
                continue

            b_str = str(b_val).strip()
            if not b_str or b_str == "0":
                continue

            is_total = any(kw in b_str for kw in ("自营总计", "外包总计", "自营外包总计", "总计"))
            if is_total:
                continue
            if b_str in ("部门/单位", "环比增减"):
                continue

            org_name = b_str
            org_code = _make_code(org_name)
            company_type = current_type if current_type else _classify_company(org_name)

            for cust_type, cols in [("cosco", (3, 4, 5, 6, 7, 9, 20, 21, 22, 23)), ("thirdparty", (10, 11, 12, 13, 14, 16, 20, 21, 22, 23))]:
                qty_col, qty_wow_col, rev_col, rev_wow_col, unit_col, move_col, total_qty_col, total_rev_col, per_capita_col, staff_col = cols
                records.append({
                    "year": target_year,
                    "week": target_week,
                    "company_type": company_type,
                    "org_name": org_name,
                    "org_code": org_code,
                    "customer_type": cust_type,
                    "container_qty": _safe_int(_cell(ws, row_idx, qty_col)),
                    "qty_wow_change": _safe_int(_cell(ws, row_idx, qty_wow_col)),
                    "revenue": _safe_float(_cell(ws, row_idx, rev_col)),
                    "rev_wow_change": _safe_float(_cell(ws, row_idx, rev_wow_col)),
                    "unit_price": _safe_float(_cell(ws, row_idx, unit_col)),
                    "move_fee": _safe_float(_cell(ws, row_idx, move_col)),
                    "total_qty": _safe_int(_cell(ws, row_idx, total_qty_col)),
                    "total_revenue": _safe_float(_cell(ws, row_idx, total_rev_col)),
                    "per_capita": _safe_float(_cell(ws, row_idx, per_capita_col)),
                    "staff_count": _safe_int(_cell(ws, row_idx, staff_col)),
                })

        return records

    def _parse_main_sheet_summaries(self) -> list[dict]:
        ws = self._find_main_sheet()
        if ws is None:
            return []
        records = self._parse_summary_rows(ws, self.year, self.week)
        self.row_counts["summaries"] = len(records)
        return records

    def _parse_summary_rows(self, ws, target_year: int, target_week: int) -> list[dict]:
        records: list[dict] = []
        in_summary_zone = False
        for row_idx in range(4, ws.max_row + 1):
            a_val = _cell(ws, row_idx, 1)
            b_val = _cell(ws, row_idx, 2)

            if a_val and "网点明细" in str(a_val):
                break
            if a_val and "全部干箱" in str(a_val):
                in_summary_zone = True
            if in_summary_zone:
                continue

            label = ""
            if b_val:
                label = str(b_val).strip()
            elif a_val:
                label = str(a_val).strip()
            if not label:
                continue

            matched_type = None
            for stype, patterns in TOTAL_PATTERNS.items():
                if any(p in label for p in patterns):
                    matched_type = stype
                    break
            if not matched_type:
                continue

            for cust_type, cols in [("cosco", (3, 4, 5, 6, 7, 9, 20, 21, 22, 23)), ("thirdparty", (10, 11, 12, 13, 14, 16, 20, 21, 22, 23))]:
                qty_col, qty_wow_col, rev_col, rev_wow_col, unit_col, move_col, total_qty_col, total_rev_col, per_capita_col, staff_col = cols
                records.append({
                    "year": target_year,
                    "week": target_week,
                    "summary_type": matched_type,
                    "customer_type": cust_type,
                    "container_qty": _safe_int(_cell(ws, row_idx, qty_col)),
                    "qty_wow_change": _safe_int(_cell(ws, row_idx, qty_wow_col)),
                    "revenue": _safe_float(_cell(ws, row_idx, rev_col)),
                    "rev_wow_change": _safe_float(_cell(ws, row_idx, rev_wow_col)),
                    "unit_price": _safe_float(_cell(ws, row_idx, unit_col)),
                    "move_fee": _safe_float(_cell(ws, row_idx, move_col)),
                    "total_qty": _safe_int(_cell(ws, row_idx, total_qty_col)),
                    "total_revenue": _safe_float(_cell(ws, row_idx, total_rev_col)),
                    "per_capita": _safe_float(_cell(ws, row_idx, per_capita_col)),
                    "staff_count": _safe_int(_cell(ws, row_idx, staff_col)),
                })

        return records

    # -- 解析周检修业务统计数据 --

    def _parse_inspection_sheet(self) -> list[dict]:
        ws = self._find_sheet("检修")
        if ws is None:
            return []

        records: list[dict] = []
        for row_idx in range(2, ws.max_row + 1):
            company_name = _cell(ws, row_idx, 1)
            site_name = _cell(ws, row_idx, 2)
            if not company_name or not site_name:
                continue

            parent_info = self._lookup_parent(str(site_name).strip())
            records.append({
                "year": self.year,
                "week": self.week,
                "site_name": str(site_name).strip(),
                "company_name": str(company_name).strip(),
                "company_type": parent_info["company_type"],
                "container_class": str(_cell(ws, row_idx, 3) or "").strip(),
                "customer_name": str(_cell(ws, row_idx, 4) or "").strip(),
                "repair_qty": _safe_int(_cell(ws, row_idx, 5)),
                "approved_amount": _safe_float(_cell(ws, row_idx, 9)),
                "move_fee": _safe_float(_cell(ws, row_idx, 12)),
            })

        self.row_counts["site_details"] = len(records)
        return records

    # -- 解析经营单位 --

    def _parse_network_sites_sheet(self) -> list[dict]:
        ws = self._find_sheet("经营单位")
        if ws is None:
            return []

        records: list[dict] = []
        for row_idx in range(2, ws.max_row + 1):
            parent_name = _cell(ws, row_idx, 1)
            site_name = _cell(ws, row_idx, 2)
            if not parent_name or not site_name:
                continue

            parent_name = str(parent_name).strip()
            site_name = str(site_name).strip()
            company_type = _classify_company(parent_name)

            code = _make_code(f"{parent_name}_{site_name}")
            parent_code = _make_code(parent_name)

            self.site_registry[site_name] = {
                "company_type": company_type,
                "parent_name": parent_name,
                "parent_code": parent_code,
            }

            records.append({
                "name": site_name,
                "code": code,
                "company_type": company_type,
                "parent_name": parent_name,
                "parent_code": parent_code,
            })

        self.row_counts["sites"] = len(records)
        return records

    def _lookup_parent(self, site_name: str) -> dict:
        if site_name in self.site_registry:
            return self.site_registry[site_name]
        for key, val in self.site_registry.items():
            if site_name in key or key in site_name:
                return val
        return {"company_type": "outsourced", "parent_name": "", "parent_code": ""}

    # -- 解析自营2026周完成情况 --

    def _parse_cumulative_sheet(self) -> list[dict]:
        ws = self._find_sheet("周完成")
        if ws is None:
            ws = self._find_sheet("完成情况")
        if ws is None:
            return []

        records: list[dict] = []
        # 定位包含 "周累计箱量" 表头的行
        header_row = None
        for row_idx in range(1, ws.max_row + 1):
            for col_idx in range(1, min(ws.max_column + 1, 10)):
                v = _cell(ws, row_idx, col_idx)
                if v and "周累计箱量" in str(v):
                    header_row = row_idx
                    break
            if header_row:
                break

        if header_row is None:
            return []

        # 读取表头下方的数据行，直到空行或非目标行
        for row_idx in range(header_row + 1, min(header_row + 10, ws.max_row + 1)):
            a_val = _cell(ws, row_idx, 1)
            if not a_val:
                break
            a_str = str(a_val).strip()
            if a_str not in SELF_ORG_NAMES and a_str not in ("自营总计", "总计", "粤西", "北部湾"):
                break

            # 简称映射
            name_map = {"粤西": "粤西运营中心", "北部湾": "北部湾运营中心"}
            org_name = name_map.get(a_str, a_str)
            org_code = _make_code(org_name)

            records.append({
                "year": self.year,
                "week": self.week,
                "org_name": org_name,
                "org_code": org_code,
                "cum_qty": _safe_int(_cell(ws, row_idx, 2)),
                "cum_qty_yoy": _safe_int(_cell(ws, row_idx, 3)),
                "cum_revenue": _safe_float(_cell(ws, row_idx, 4)),
                "cum_revenue_yoy": _safe_float(_cell(ws, row_idx, 5)),
            })

        self.row_counts["cumulative"] = len(records)
        return records

    def _get_yoy_year_week(self) -> tuple[int, int]:
        return self.year - 1, self.week - 1


# ---------------------------------------------------------------------------
# 数据库写入
# ---------------------------------------------------------------------------


async def import_weekly_excel(
    db: AsyncSession,
    file_path: str | Path,
    year: int,
    week: int,
    filename: str = "",
    yoy_sheet: str | None = None,
) -> dict:
    log = ExcelUploadLog(
        year=year,
        week=week,
        filename=filename,
        status="pending",
        uploaded_at=datetime.now(),
    )
    db.add(log)
    await db.flush()

    try:
        importer = WeeklyExcelImporter(file_path, year, week)

        sites_data = importer._parse_network_sites_sheet()
        data = importer.parse_all()

        # 清除旧数据（幂等）
        for table in [
            RepairWeeklyOrg,
            RepairWeeklySummary,
            RepairWeeklySiteDetail,
            RepairWeeklyCumulative,
        ]:
            await db.execute(
                delete(table).where(table.year == year, table.week == week)
            )

        # 网点主数据 upsert
        for s in sites_data:
            existing = await db.execute(
                select(RepairNetworkSite).where(
                    RepairNetworkSite.code == s["code"]
                )
            )
            obj = existing.scalar_one_or_none()
            if obj:
                obj.name = s["name"]
                obj.company_type = s["company_type"]
                obj.parent_name = s["parent_name"]
                obj.parent_code = s["parent_code"]
            else:
                db.add(RepairNetworkSite(**s))

        # 机构数据
        for r in data["orgs"]:
            db.add(RepairWeeklyOrg(**r))

        # 汇总数据
        for r in data["summaries"]:
            db.add(RepairWeeklySummary(**r))

        # 网点明细
        for r in data["site_details"]:
            db.add(RepairWeeklySiteDetail(**r))

        # 累计数据
        for r in data["cumulative"]:
            db.add(RepairWeeklyCumulative(**r))

        # 同比数据导入
        yoy_counts: dict[str, int] = {}
        if yoy_sheet:
            prev_year, prev_week = year - 1, week - 1
            yoy_data = importer.parse_yoy(yoy_sheet)

            for table in [RepairWeeklyOrg, RepairWeeklySummary]:
                await db.execute(
                    delete(table).where(table.year == prev_year, table.week == prev_week)
                )

            for r in yoy_data["yoy_orgs"]:
                db.add(RepairWeeklyOrg(**r))
            for r in yoy_data["yoy_summaries"]:
                db.add(RepairWeeklySummary(**r))

            yoy_counts = {
                "yoy_orgs": len(yoy_data["yoy_orgs"]),
                "yoy_summaries": len(yoy_data["yoy_summaries"]),
                "yoy_year": prev_year,
                "yoy_week": prev_week,
            }

        log.status = "success"
        log.row_counts = json.dumps({**importer.row_counts, **yoy_counts}, ensure_ascii=False)
        log.processed_at = datetime.now()
        await db.flush()

        return {
            "status": "success",
            "year": year,
            "week": week,
            "row_counts": {**importer.row_counts, **yoy_counts},
        }

    except Exception as exc:
        log.status = "error"
        log.error_message = str(exc)
        log.processed_at = datetime.now()
        await db.flush()
        raise
