import { defineStore } from "pinia";
import { ref } from "vue";
import { ElMessage } from "element-plus";

import {
  getCargoDistribution,
  getFlowOD,
  getKpiOverview,
  getRecentAlerts,
  getThroughputTrend,
  getYards,
  getYardRanking,
} from "@/api/dashboard";

export interface YardItem {
  id: number;
  name: string;
  code: string;
  province: string;
  city: string;
  lng: number;
  lat: number;
  capacity: number;
  status: string;
}

export const useYardStore = defineStore("yard", () => {
  const loading = ref(false);
  const loadError = ref<string | null>(null);
  const yards = ref<YardItem[]>([]);
  const geojson = ref<any>(null);
  const kpi = ref({ yard_count: 0, total_stock_teu: 0, today_throughput: 0, in_transit_vehicles: 0 });
  const throughput = ref<any[]>([]);
  const cargoItems = ref<any[]>([]);
  const rankingItems = ref<any[]>([]);
  const alerts = ref<any[]>([]);
  const odFlow = ref<any[]>([]);

  const loadAll = async (province?: string | null) => {
    loading.value = true;
    loadError.value = null;
    try {
      const [yardsRes, kpiRes, trendRes, cargoRes, rankRes, alertsRes, odRes] = await Promise.all([
        getYards(province || undefined),
        getKpiOverview(),
        getThroughputTrend(),
        getCargoDistribution(),
        getYardRanking(10, province || undefined),
        getRecentAlerts(),
        getFlowOD(),
      ]);

      yards.value = yardsRes.items;
      geojson.value = yardsRes.geojson;
      kpi.value = kpiRes;
      throughput.value = trendRes.points;
      cargoItems.value = cargoRes.items;
      rankingItems.value = rankRes.items;
      alerts.value = alertsRes.items;
      odFlow.value = odRes.items;
    } catch (e: any) {
      const msg =
        e?.response?.data?.detail ||
        e?.message ||
        "接口请求失败：请先在本机启动后端（backend，默认 http://127.0.0.1:8000），并确认 Vite 代理可用";
      loadError.value = String(msg);
      console.error("[yard] loadAll failed", e);
      ElMessage.error(loadError.value);
    } finally {
      loading.value = false;
    }
  };

  return {
    loading,
    loadError,
    yards,
    geojson,
    kpi,
    throughput,
    cargoItems,
    rankingItems,
    alerts,
    odFlow,
    loadAll,
  };
});
