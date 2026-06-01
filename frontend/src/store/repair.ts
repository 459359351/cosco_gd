import { defineStore } from "pinia";
import { ref } from "vue";
import { ElMessage } from "element-plus";

import {
  getRepairCumulative,
  getRepairCustomerDist,
  getRepairKpi,
  getRepairOrgRanking,
  getRepairSiteDrilldown,
  getNetworkSites,
} from "@/api/repairDashboard";
import type { NetworkSite } from "@/api/repairDashboard";

export interface RepairKpiBlock {
  container_qty: number;
  qty_wow: number;
  revenue: number;
  rev_wow: number;
  qty_yoy: number | null;
  rev_yoy: number | null;
}

export interface OrgRankItem {
  org_name: string;
  org_code: string;
  company_type: string;
  container_qty: number;
  revenue: number;
  qty_wow: number;
  rev_wow: number;
  total_qty: number;
  total_revenue: number;
}

export interface SiteDrilldownItem {
  site_name: string;
  repair_qty: number;
  approved_amount: number;
  customer_names: string[];
  pct: number;
}

export interface CustomerDistItem {
  customer_type: string;
  container_qty: number;
  revenue: number;
  pct_qty: number;
  pct_rev: number;
}

export type CompanyFilter = "all" | "self" | "outsourced";
export type MapRenderMode = "point" | "heat" | "3d";
export type MapViewMode = "aggregate" | "drilldown";
export type RegionFilter = "all" | "guangdong" | "guangxi";

export const useRepairStore = defineStore("repair", () => {
  const loading = ref(false);
  const year = ref(2026);
  const week = ref(20);

  const kpi = ref<{
    self_: RepairKpiBlock;
    outsourced: RepairKpiBlock;
    thirdparty: RepairKpiBlock;
    cosco: RepairKpiBlock;
    total: RepairKpiBlock;
    week_label: string;
  } | null>(null);

  const selfOrgs = ref<OrgRankItem[]>([]);
  const outsourcedOrgs = ref<OrgRankItem[]>([]);
  const selectedParent = ref<string | null>(null);
  const selectedCompanyType = ref<string>("self");
  const siteDetails = ref<SiteDrilldownItem[]>([]);
  const customerDist = ref<CustomerDistItem[]>([]);
  const cumulative = ref<any[]>([]);
  const sites = ref<NetworkSite[]>([]);

  /* ---------- 地图统一状态 ---------- */
  const viewMode = ref<MapViewMode>("aggregate");
  const companyFilter = ref<CompanyFilter>("all");
  const renderMode = ref<MapRenderMode>("point");
  const regionFilter = ref<RegionFilter>("all");

  const loadAll = async () => {
    loading.value = true;
    try {
      const [kpiRes, selfRes, outRes, custRes, cumRes, sitesRes] = await Promise.all([
        getRepairKpi(year.value, week.value),
        getRepairOrgRanking("self", "revenue", 10, year.value, week.value),
        getRepairOrgRanking("outsourced", "revenue", 10, year.value, week.value),
        getRepairCustomerDist(year.value, week.value),
        getRepairCumulative(year.value, week.value),
        getNetworkSites(),
      ]);

      kpi.value = kpiRes;
      selfOrgs.value = selfRes;
      outsourcedOrgs.value = outRes;
      customerDist.value = custRes;
      cumulative.value = cumRes;
      sites.value = sitesRes;
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || "修理业务数据加载失败";
      console.error("[repair] loadAll failed", e);
      ElMessage.error(String(msg));
    } finally {
      loading.value = false;
    }
  };

  const drilldown = async (parentName: string) => {
    /* 幂等：同一机构不重复触发 */
    if (parentName === selectedParent.value) return;

    selectedParent.value = parentName;
    viewMode.value = "drilldown";
    try {
      const res = await getRepairSiteDrilldown(parentName, year.value, week.value);
      siteDetails.value = res.items || [];
      selectedCompanyType.value = res.company_type || "self";
    } catch (e: any) {
      console.error("[repair] drilldown failed", e);
      ElMessage.error("网点明细加载失败");
    }
  };

  const clearDrilldown = () => {
    selectedParent.value = null;
    siteDetails.value = [];
    viewMode.value = "aggregate";
  };

  const switchView = (mode: MapViewMode) => {
    viewMode.value = mode;
    if (mode === "aggregate") {
      selectedParent.value = null;
      siteDetails.value = [];
    }
  };

  return {
    loading,
    year,
    week,
    kpi,
    selfOrgs,
    outsourcedOrgs,
    selectedParent,
    selectedCompanyType,
    siteDetails,
    customerDist,
    cumulative,
    sites,
    viewMode,
    companyFilter,
    renderMode,
    regionFilter,
    loadAll,
    drilldown,
    clearDrilldown,
    switchView,
  };
});
