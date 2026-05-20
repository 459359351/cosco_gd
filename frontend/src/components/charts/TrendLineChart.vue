<template>
  <VChart class="chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { computed } from "vue";
import VChart from "vue-echarts";

import { useYardStore } from "@/store/yard";

const store = useYardStore();
const option = computed(() => ({
  tooltip: { trigger: "axis" },
  grid: { top: 24, right: 20, left: 46, bottom: 24 },
  xAxis: { type: "category", data: store.throughput.map((x) => x.date), axisLabel: { color: "#8eb8e2" } },
  yAxis: { type: "value", axisLabel: { color: "#8eb8e2" } },
  series: [
    {
      type: "line",
      smooth: true,
      data: store.throughput.map((x) => x.in_teu),
      lineStyle: { color: "#30deff", width: 2 },
      areaStyle: {
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 0,
          y2: 1,
          colorStops: [
            { offset: 0, color: "rgba(39,219,255,0.48)" },
            { offset: 1, color: "rgba(39,219,255,0.03)" },
          ],
        },
      },
    },
  ],
}));
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>
