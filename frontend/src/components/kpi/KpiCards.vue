<template>
  <div class="cards">
    <div v-for="card in cards" :key="card.label" class="card">
      <div class="label">{{ card.label }}</div>
      <div class="value">{{ card.value }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import gsap from "gsap";
import { computed } from "vue";
import { reactive, watch } from "vue";

import { useYardStore } from "@/store/yard";

const yardStore = useYardStore();
const display = reactive({
  yard_count: 0,
  total_stock_teu: 0,
  today_throughput: 0,
  in_transit_vehicles: 0,
});

watch(
  () => yardStore.kpi,
  (kpi) => {
    gsap.to(display, { ...kpi, duration: 0.8, ease: "power2.out", roundProps: "all" });
  },
  { deep: true, immediate: true },
);

const cards = computed(() => [
  { label: "堆场总数", value: Math.round(display.yard_count) },
  { label: "在场库存TEU", value: Math.round(display.total_stock_teu) },
  { label: "今日吞吐", value: Math.round(display.today_throughput) },
  { label: "在途车辆", value: Math.round(display.in_transit_vehicles) },
]);
</script>

<style scoped lang="scss">
.cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  padding: 12px;
}
.card {
  padding: 12px;
  border: 1px solid rgba(87, 233, 255, 0.32);
  background: rgba(13, 43, 79, 0.68);
}
.label {
  color: #78c9ff;
  font-size: 12px;
}
.value {
  margin-top: 8px;
  font-size: 24px;
  color: #a7fbff;
}
</style>
