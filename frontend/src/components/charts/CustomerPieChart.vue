<template>
  <div class="customer-pie">
    <div class="pie-header">
      <span>客户类型收入占比</span>
      <div class="metric-switch">
        <button :class="{ active: metric === 'revenue' }" @click="metric = 'revenue'">收入</button>
        <button :class="{ active: metric === 'qty' }" @click="metric = 'qty'">箱量</button>
      </div>
    </div>
    <div class="pie-body" ref="chartRef" />
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
  if (!chart) return;
  chart.setOption({
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} ({d}%)",
    },
    series: [
      {
        type: "pie",
        radius: ["40%", "70%"],
        center: ["50%", "55%"],
        data: pieData.value.map((d) => ({
          name: d.name,
          value: d.value,
          itemStyle: { color: d.color },
        })),
        label: {
          color: "#a7fbff",
          fontSize: 12,
          formatter: "{b}\n{d}%",
        },
        labelLine: {
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

onMounted(() => {
  if (chartRef.value) {
    chart = echarts.init(chartRef.value);
    render();
  }
});

onUnmounted(() => {
  chart?.dispose();
});
</script>

<style scoped lang="scss">
.customer-pie {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
}
.pie-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #a7fbff;
  margin-bottom: 4px;
}
.metric-switch {
  display: flex;
  gap: 2px;
  button {
    padding: 2px 8px;
    font-size: 11px;
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
.pie-body {
  flex: 1;
  min-height: 0;
}
</style>
