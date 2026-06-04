import { defineStore } from "pinia";
import { ref, computed } from "vue";

import { getAvailableWeeks, getRepairKpi } from "@/api/repairDashboard";
import type { AvailableWeekItem } from "@/api/repairDashboard";
import type { RepairKpiBlock } from "@/store/repair";
import { useRepairStore } from "@/store/repair";

/** KPI 预览数据结构（与后端 RepairKpiOverview 对应） */
interface KpiOverview {
  self_: RepairKpiBlock;
  outsourced: RepairKpiBlock;
  thirdparty: RepairKpiBlock;
  cosco: RepairKpiBlock;
  total: RepairKpiBlock;
  week_label: string;
}

export const useWeekStore = defineStore("week", () => {
  /* ---------- 可用周列表 ---------- */
  const weeks = ref<AvailableWeekItem[]>([]);
  const latestWeek = ref<AvailableWeekItem | null>(null);
  const loaded = ref(false);

  /* ---------- Hover 预览缓存 ---------- */
  const previewCache = ref<Map<string, KpiOverview>>(new Map());
  const hoveredWeek = ref<AvailableWeekItem | null>(null);
  const previewData = ref<KpiOverview | null>(null);
  const previewLoading = ref(false);

  /* ---------- 当前选中周 ---------- */
  const selectedYear = ref(2026);
  const selectedWeek = ref(20);

  /** 当前选中的标签文本 */
  const selectedLabel = computed(() => {
    if (!loaded.value || weeks.value.length === 0) return `${selectedYear.value}年第${selectedWeek.value}周`;
    const found = weeks.value.find(
      (w) => w.year === selectedYear.value && w.week === selectedWeek.value,
    );
    return found ? found.week_label : `${selectedYear.value}年第${selectedWeek.value}周`;
  });

  const selectedDateRange = computed(() => {
    const found = weeks.value.find(
      (w) => w.year === selectedYear.value && w.week === selectedWeek.value,
    );
    return found?.date_range ?? "";
  });

  /* ---------- 获取可用周列表 ---------- */
  async function fetchWeeks(limit = 12) {
    const data = await getAvailableWeeks(limit);
    weeks.value = data.weeks;
    latestWeek.value = data.latest;
    loaded.value = true;
  }

  /* ---------- 获取 hover 的 KPI 预览（带缓存） ---------- */
  async function fetchPreview(year: number, week: number) {
    const key = `${year}-${week}`;
    if (previewCache.value.has(key)) {
      previewData.value = previewCache.value.get(key);
      return;
    }
    previewLoading.value = true;
    try {
      const kpi = await getRepairKpi(year, week);
      previewCache.value.set(key, kpi);
      previewData.value = kpi;
    } catch {
      previewData.value = null;
    } finally {
      previewLoading.value = false;
    }
  }

  /* ---------- 清除 hover 状态 ---------- */
  function clearHover() {
    hoveredWeek.value = null;
    previewData.value = null;
  }

  /* ---------- 选中某周，刷新全局数据 ---------- */
  function selectWeek(year: number, week: number) {
    selectedYear.value = year;
    selectedWeek.value = week;
    const repairStore = useRepairStore();
    repairStore.year = year;
    repairStore.week = week;
    repairStore.loadAll();
  }

  return {
    weeks,
    latestWeek,
    loaded,
    previewCache,
    hoveredWeek,
    previewData,
    previewLoading,
    selectedYear,
    selectedWeek,
    selectedLabel,
    selectedDateRange,
    fetchWeeks,
    fetchPreview,
    clearHover,
    selectWeek,
  };
});
