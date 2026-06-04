import api from "@/api/client";

export const getRepairKpi = (year = 2026, week = 20) =>
  api.get("/repair/kpi", { params: { year, week } }).then((r) => r.data);

export const getRepairOrgRanking = (
  companyType = "self",
  metric = "revenue",
  top = 10,
  year = 2026,
  week = 20,
) =>
  api
    .get("/repair/org-ranking", { params: { company_type: companyType, metric, top, year, week } })
    .then((r) => r.data);

export const getRepairSiteDrilldown = (parentName: string, year = 2026, week = 20) =>
  api.get("/repair/site-drilldown", { params: { parent_name: parentName, year, week } }).then((r) => r.data);

export const getRepairCustomerDist = (year = 2026, week = 20) =>
  api.get("/repair/customer-dist", { params: { year, week } }).then((r) => r.data);

export const getRepairCumulative = (year = 2026, week = 20) =>
  api.get("/repair/cumulative", { params: { year, week } }).then((r) => r.data);

export const getNetworkSites = () =>
  api.get("/repair/network-sites").then((r) => r.data as NetworkSite[]);

export interface NetworkSite {
  name: string;
  code: string;
  company_type: string;
  parent_name: string;
  province: string;
  city: string;
  lng: number;
  lat: number;
  distance: number;
  status: string;
}

export const uploadWeeklyExcel = (file: File, year: number, week: number, yoySheet?: string) => {
  const fd = new FormData();
  fd.append("file", file);
  const params = new URLSearchParams({ year: String(year), week: String(week) });
  if (yoySheet) params.set("yoy_sheet", yoySheet);
  return api
    .post(`/data-console/excel/weekly-import?${params}`, fd)
    .then((r) => r.data);
};

export const previewExcelSheets = (file: File, year: number, week: number) => {
  const fd = new FormData();
  fd.append("file", file);
  return api
    .post(`/data-console/excel/preview-sheets?year=${year}&week=${week}`, fd)
    .then((r) => r.data as { filename: string; sheets: SheetInfo[] });
};

export interface SheetInfo {
  name: string;
  detected_year: number | null;
  detected_week: number | null;
  suggested_role: string | null;
}

export const batchUpdateSiteCoords = (
  items: Array<{ code: string; lng: number; lat: number; province?: string; city?: string }>,
) => api.post("/repair/network-sites/geocode", items).then((r) => r.data);

export interface AvailableWeekItem {
  year: number;
  week: number;
  week_label: string;
  date_range: string;
}

export const getAvailableWeeks = (limit = 12) =>
  api
    .get("/repair/available-weeks", { params: { limit } })
    .then(
      (r) =>
        r.data as {
          weeks: AvailableWeekItem[];
          latest: AvailableWeekItem | null;
        },
    );
