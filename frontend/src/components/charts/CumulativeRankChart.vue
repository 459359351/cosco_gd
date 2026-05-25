<template>
  <div class="cumulative-ranking">
    <div class="ranking-header">
      <div class="switch-btns">
        <button :class="{ active: metric === 'qty' }" @click="metric = 'qty'">累计修理量</button>
        <button :class="{ active: metric === 'revenue' }" @click="metric = 'revenue'">累计收入</button>
      </div>
    </div>
    <div class="ranking-body" ref="scrollRef">
      <div class="ranking-scroll" v-for="round in 2" :key="round">
        <div
          v-for="(item, idx) in list"
          :key="round + '-' + item.org_name"
          class="ranking-row"
        >
          <span class="rank" :class="{ top3: idx < 3 }">{{ idx + 1 }}</span>
          <span class="name" :title="item.org_name">{{ item.org_name }}</span>
          <span class="bar-wrap">
            <span class="bar" :style="{ width: barWidth(item) + '%' }" />
          </span>
          <span class="value">{{ formatVal(item) }}</span>
          <span class="yoy" :class="{ up: yoyVal(item) > 0, down: yoyVal(item) < 0 }">
            {{ yoyVal(item) > 0 ? '+' : '' }}{{ formatYoy(item) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();
const metric = ref<"qty" | "revenue">("qty");
const scrollRef = ref<HTMLElement | null>(null);
let scrollRaf: number | null = null;

const list = computed(() => store.cumulative || []);

const maxVal = computed(() => {
  if (!list.value.length) return 1;
  const vals = list.value.map((i: any) =>
    metric.value === "qty" ? i.cum_qty : i.cum_revenue,
  );
  return Math.max(...vals) || 1;
});

function barWidth(item: any) {
  const v = metric.value === "qty" ? item.cum_qty : item.cum_revenue;
  return (v / maxVal.value) * 100;
}

function formatVal(item: any) {
  if (metric.value === "qty") return item.cum_qty.toLocaleString();
  return item.cum_revenue.toFixed(1) + "万";
}

function yoyVal(item: any) {
  return metric.value === "qty" ? item.cum_qty_yoy : item.cum_revenue_yoy;
}

function formatYoy(item: any) {
  const v = yoyVal(item);
  if (v == null) return "-";
  if (metric.value === "qty") return v.toLocaleString();
  return v.toFixed(1) + "万";
}

function startAutoScroll() {
  stopAutoScroll();
  const body = scrollRef.value;
  if (!body) return;
  body.scrollTop = 0;
  const speed = 0.25;
  let acc = 0;

  const step = () => {
    if (!body) return;
    acc += speed;
    if (acc >= 1) {
      acc -= 1;
      const halfH = body.scrollHeight / 2;
      body.scrollTop += 1;
      if (body.scrollTop >= halfH) {
        body.scrollTop = 0;
      }
    }
    scrollRaf = requestAnimationFrame(step);
  };
  scrollRaf = requestAnimationFrame(step);
}

function stopAutoScroll() {
  if (scrollRaf !== null) {
    cancelAnimationFrame(scrollRaf);
    scrollRaf = null;
  }
}

watch(list, async () => {
  stopAutoScroll();
  await nextTick();
  startAutoScroll();
});

onMounted(() => {
  startAutoScroll();
});

onBeforeUnmount(() => {
  stopAutoScroll();
});
</script>

<style scoped lang="scss">
.cumulative-ranking {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
}
.ranking-header {
  margin-bottom: 8px;
}
.switch-btns {
  display: flex;
  gap: 4px;
  button {
    flex: 1;
    padding: 4px 8px;
    font-size: 12px;
    border: 1px solid rgba(57, 216, 255, 0.3);
    background: transparent;
    color: rgba(168, 201, 255, 0.7);
    border-radius: 4px;
    cursor: pointer;
    &.active {
      background: rgba(0, 212, 255, 0.15);
      border-color: #00d4ff;
      color: #00d4ff;
    }
  }
}
.ranking-body {
  flex: 1;
  overflow: auto;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
.ranking-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 4px;
}
.rank {
  width: 20px;
  text-align: center;
  font-size: 12px;
  color: rgba(168, 201, 255, 0.5);
  &.top3 {
    color: #ffc107;
    font-weight: 700;
  }
}
.name {
  width: 80px;
  font-size: 12px;
  color: #a7fbff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.bar-wrap {
  flex: 1;
  height: 8px;
  background: rgba(57, 216, 255, 0.1);
  border-radius: 4px;
  overflow: hidden;
}
.bar {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #00d4ff, #0090ff);
  border-radius: 4px;
  transition: width 0.5s ease;
}
.value {
  width: 55px;
  text-align: right;
  font-size: 12px;
  color: #e0f0ff;
}
.yoy {
  width: 50px;
  text-align: right;
  font-size: 11px;
  color: rgba(168, 201, 255, 0.5);
  &.up {
    color: #2ecc71;
  }
  &.down {
    color: #e74c3c;
  }
}
</style>
