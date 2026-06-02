<template>
  <div class="customer-pie">
    <div class="pie-header">
      <span>客户类型占比</span>
      <div class="metric-switch">
        <button :class="{ active: metric === 'revenue' }" @click="metric = 'revenue'">收入</button>
        <button :class="{ active: metric === 'qty' }" @click="metric = 'qty'">箱量</button>
      </div>
    </div>
    <div class="pie-content">
      <div class="pie-body" ref="chartRef" />
      <div class="pie-legend">
        <div
          v-for="item in pieData"
          :key="item.name"
          class="legend-item"
        >
          <span class="legend-dot" :style="{ background: item.color }" />
          <span class="legend-name">{{ item.name }}</span>
          <span class="legend-pct">{{ item.pct }}%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import * as echarts from "echarts";
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();
const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;
const metric = ref<"revenue" | "qty">("revenue");

const colors: Record<string, string> = {
  cosco: "#00d4ff",
  thirdparty: "#2ecc71",
};

const labels: Record<string, string> = {
  cosco: "中远海",
  thirdparty: "第三方",
};

const pieData = computed(() => {
  return store.customerDist.map((d) => ({
    name: labels[d.customer_type] || d.customer_type,
    value: metric.value === "revenue" ? d.revenue : d.container_qty,
    pct: metric.value === "revenue" ? d.pct_rev : d.pct_qty,
    color: colors[d.customer_type] || "#999",
  }));
});

function render() {
  if (!chart || !chartRef.value) return;
  const w = chartRef.value.clientWidth;
  const h = chartRef.value.clientHeight;
  // 基于容器最小尺寸计算字体，确保标签在任意分辨率下不溢出
  const labelFont = Math.max(9, Math.min(12, Math.round(Math.min(w, h) / 26)));
  chart.setOption({
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
    },
    series: [
      {
        type: "pie",
        radius: ["30%", "42%"],
        center: ["40%", "50%"],
        data: pieData.value.map((d) => ({
          name: d.name,
          value: d.value,
          itemStyle: { color: d.color },
        })),
        label: {
          color: "#a7fbff",
          fontSize: labelFont,
          formatter: "{b}  {d}%",
        },
        labelLine: {
          length: Math.max(8, Math.round(w * 0.035)),
          length2: Math.max(4, Math.round(w * 0.04)),
          lineStyle: { color: "rgba(57, 216, 255, 0.4)" },
        },
        emphasis: {
          itemStyle: { shadowBlur: 10, shadowColor: "rgba(0, 0, 0, 0.5)" },
        },
      },
    ],
  });
}

watch(pieData, () => nextTick(render));
watch(metric, () => nextTick(render));

function onResize() {
  chart?.resize();
}

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value);
    render();
  }
  window.addEventListener("resize", onResize);
});

onUnmounted(() => {
  window.removeEventListener("resize", onResize);
  chart?.dispose();
});
</script>

<style scoped lang="scss">
.customer-pie {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: max(2px, 0.28vh) max(6px, 0.42vw);
}
.pie-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: clamp(11px, 0.68vw, 13px);
  color: #a7fbff;
  margin-bottom: 0;
  flex-shrink: 0;
}
.metric-switch {
  display: flex;
  gap: max(1px, 0.1vw);
  button {
    padding: max(1px, 0.19vh) max(4px, 0.42vw);
    font-size: clamp(10px, 0.57vw, 12px);
    border: 1px solid rgba(57, 216, 255, 0.3);
    background: transparent;
    color: rgba(168, 201, 255, 0.5);
    border-radius: 3px;
    cursor: pointer;
    &.active {
      background: rgba(0, 212, 255, 0.15);
      color: #00d4ff;
    }
  }
}
.pie-content {
  flex: 1;
  display: flex;
  align-items: center;
  min-height: 0;
}
.pie-body {
  flex: 1.2;
  height: 100%;
  min-height: 0;
  overflow: visible;
}
.pie-legend {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: max(10px, 1.5vh);
  padding-right: max(6px, 0.5vw);
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: clamp(10px, 0.7vw, 13px);
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 2px;
  flex-shrink: 0;
}
.legend-name {
  color: rgba(168, 201, 255, 0.75);
  flex: 1;
}
.legend-pct {
  color: #e0f0ff;
  font-weight: 700;
  font-size: clamp(12px, 0.9vw, 15px);
}
</style>
