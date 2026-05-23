import { defineStore } from "pinia";
import { ref } from "vue";
import { ElMessage } from "element-plus";

import {
  getRepairCumulative,
  getRepairCustomerDist,
  getRepairKpi,
  getRepairOrgRanking,
  getRepairSiteDrilldown,
} from "@/api/repairDashboard";

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

export const useRepairStore = defineStore("repair", () => {
  const loading = ref(false);
  const year = ref(2026);
  const week = ref(20);

  const kpi = ref<{
    self_: RepairKpiBlock;
    outsourced: RepairKpiBlock;
    thirdparty: RepairKpiBlock;
    week_label: string;
  } | null>(null);

  const selfOrgs = ref<OrgRankItem[]>([]);
  const outsourcedOrgs = ref<OrgRankItem[]>([]);
  const selectedParent = ref<string | null>(null);
  const selectedCompanyType = ref<string>("self");
  const siteDetails = ref<SiteDrilldownItem[]>([]);
  const customerDist = ref<CustomerDistItem[]>([]);
  const cumulative = ref<any[]>([]);

  const loadAll = async () => {
    loading.value = true;
    try {
      const [kpiRes, selfRes, outRes, custRes, cumRes] = await Promise.all([
        getRepairKpi(year.value, week.value),
        getRepairOrgRanking("self", "revenue", 10, year.value, week.value),
        getRepairOrgRanking("outsourced", "revenue", 10, year.value, week.value),
        getRepairCustomerDist(year.value, week.value),
        getRepairCumulative(year.value, week.value),
      ]);

      kpi.value = kpiRes;
      selfOrgs.value = selfRes;
      outsourcedOrgs.value = outRes;
      customerDist.value = custRes;
      cumulative.value = cumRes;

      if (selfRes.length > 0 && !selectedParent.value) {
        await drilldown(selfRes[0].org_name);
      }
    } catch (e: any) {
      const msg = e?.response?.data?.detail || e?.message || "修理业务数据加载失败";
      console.error("[repair] loadAll failed", e);
      ElMessage.error(String(msg));
    } finally {
      loading.value = false;
    }
  };

  const drilldown = async (parentName: string) => {
    selectedParent.value = parentName;
    try {
      const res = await getRepairSiteDrilldown(parentName, year.value, week.value);
      siteDetails.value = res.items || [];
      selectedCompanyType.value = res.company_type || "self";
    } catch (e: any) {
      console.error("[repair] drilldown failed", e);
      ElMessage.error("网点明细加载失败");
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
    loadAll,
    drilldown,
  };
});
