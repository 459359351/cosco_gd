<template>
  <VChart class="chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { computed } from "vue";
import VChart from "vue-echarts";

import { useYardStore } from "@/store/yard";

const yardStore = useYardStore();
const option = computed(() => ({
  grid: { top: 24, right: 20, left: 80, bottom: 20 },
  xAxis: {
    type: "value",
    axisLabel: { color: "#8eb8e2" },
  },
  yAxis: {
    type: "category",
    data: yardStore.rankingItems.map((item) => item.name),
    axisLabel: { color: "#8eb8e2" },
  },
  series: [
    {
      type: "bar",
      data: yardStore.rankingItems.map((item) => item.capacity),
      itemStyle: {
        color: {
          type: "linear",
          x: 0,
          y: 0,
          x2: 1,
          y2: 0,
          colorStops: [
            { offset: 0, color: "#31d8ff" },
            { offset: 1, color: "#3689ff" },
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
