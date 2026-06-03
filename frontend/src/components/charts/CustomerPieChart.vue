<template>
  <div class="customer-pie">
    <div class="pie-dual">
      <div class="pie-half">
        <div class="pie-half-title">收入占比</div>
        <div class="pie-half-body" ref="chartRefRev" />
      </div>
      <div class="pie-half">
        <div class="pie-half-title">箱量占比</div>
        <div class="pie-half-body" ref="chartRefQty" />
      </div>
    </div>
    <div class="pie-legend-shared">
      <div v-for="item in legendData" :key="item.name" class="legend-item">
        <span class="legend-dot" :style="{ background: item.color }" />
        <span class="legend-name">{{ item.name }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();
const chartRefRev = ref<HTMLElement>();
const chartRefQty = ref<HTMLElement>();
let chartRev: echarts.ECharts | null = null;
let chartQty: echarts.ECharts | null = null;

const colors: Record<string, string> = {
  cosco: "#00d4ff",
  thirdparty: "#2ecc71",
};

const labels: Record<string, string> = {
  cosco: "中远海",
  thirdparty: "第三方",
};

const legendData = computed(() =>
  store.customerDist.map((d) => ({
    name: labels[d.customer_type] || d.customer_type,
    color: colors[d.customer_type] || "#999",
  })),
);

function renderRev() {
  if (!chartRev || !chartRefRev.value) return;
  const data = store.customerDist.map((d) => ({
    name: labels[d.customer_type] || d.customer_type,
    value: d.revenue,
    itemStyle: { color: colors[d.customer_type] || "#999" },
  }));
  chartRev.setOption({
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    series: [
      {
        type: "pie",
        radius: ["22%", "80%"],
        center: ["50%", "48%"],
        data,
        label: {
          show: true,
          position: "inside",
          formatter: "{d}%",
          fontSize: 12,
          color: "#fff",
          fontWeight: 700,
        },
        labelLine: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: "rgba(0, 0, 0, 0.5)" },
        },
      },
    ],
  });
}

function renderQty() {
  if (!chartQty || !chartRefQty.value) return;
  const data = store.customerDist.map((d) => ({
    name: labels[d.customer_type] || d.customer_type,
    value: d.container_qty,
    itemStyle: { color: colors[d.customer_type] || "#999" },
  }));
  chartQty.setOption({
    tooltip: { trigger: "item", formatter: "{b}: {c} ({d}%)" },
    series: [
      {
        type: "pie",
        radius: ["22%", "80%"],
        center: ["50%", "48%"],
        data,
        label: {
          show: true,
          position: "inside",
          formatter: "{d}%",
          fontSize: 12,
          color: "#fff",
          fontWeight: 700,
        },
        labelLine: { show: false },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: "rgba(0, 0, 0, 0.5)" },
        },
      },
    ],
  });
}

function renderAll() {
  nextTick(() => {
    renderRev();
    renderQty();
  });
}

watch(() => store.customerDist, renderAll, { deep: true });

function onResize() {
  chartRev?.resize();
  chartQty?.resize();
}

onMounted(() => {
  if (chartRefRev.value) {
    chartRev = echarts.init(chartRefRev.value);
  }
  if (chartRefQty.value) {
    chartQty = echarts.init(chartRefQty.value);
  }
  renderAll();
  window.addEventListener("resize", onResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", onResize);
  chartRev?.dispose();
  chartQty?.dispose();
});
</script>

<style scoped lang="scss">
.customer-pie {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: max(2px, 0.28vh) max(4px, 0.3vw);
}
.pie-dual {
  flex: 1;
  display: flex;
  flex-direction: row;
  gap: max(4px, 0.4vw);
  min-height: 0;
}
.pie-half {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.pie-half-title {
  font-size: clamp(10px, 0.65vw, 12px);
  color: #78c9ff;
  text-align: center;
  flex-shrink: 0;
  margin-bottom: max(2px, 0.2vh);
}
.pie-half-body {
  flex: 1;
  min-height: 0;
}
.pie-legend-shared {
  display: flex;
  justify-content: center;
  gap: max(16px, 2vw);
  padding: max(4px, 0.4vh) 0;
  flex-shrink: 0;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: clamp(11px, 0.75vw, 13px);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}
.legend-name {
  color: rgba(168, 201, 255, 0.8);
}
</style>
