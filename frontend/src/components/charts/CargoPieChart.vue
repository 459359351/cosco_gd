<template>
  <VChart class="chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { computed } from "vue";
import VChart from "vue-echarts";

import { useYardStore } from "@/store/yard";

const store = useYardStore();
const option = computed(() => ({
  tooltip: { trigger: "item" },
  legend: { bottom: 0, textStyle: { color: "#8eb8e2" } },
  series: [
    {
      type: "pie",
      radius: ["26%", "62%"],
      roseType: "radius",
      label: { color: "#bdeaff" },
      data: store.cargoItems.map((x) => ({ name: x.category, value: x.volume })),
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
