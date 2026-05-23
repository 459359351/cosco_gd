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

export const uploadWeeklyExcel = (file: File, year: number, week: number) => {
  const fd = new FormData();
  fd.append("file", file);
  return api
    .post(`/data-console/excel/weekly-import?year=${year}&week=${week}`, fd)
    .then((r) => r.data);
};
