<template>
  <VChart class="chart" :option="option" autoresize />
</template>

<script setup lang="ts">
import { computed } from "vue";
import VChart from "vue-echarts";

import { useYardStore } from "@/store/yard";

const store = useYardStore();
const option = computed(() => {
  const busy = store.yards.filter((x) => x.status !== "normal").length;
  const ratio = store.yards.length ? Math.round((busy / store.yards.length) * 100) : 0;
  return {
    series: [
      {
        type: "gauge",
        progress: { show: true, width: 12 },
        detail: { valueAnimation: true, formatter: "{value}%", color: "#a7fbff" },
        axisLabel: { color: "#8eb8e2" },
        data: [{ value: ratio, name: "繁忙占比" }],
      },
    ],
  };
});
</script>

<style scoped>
.chart {
  width: 100%;
  height: 100%;
}
</style>
