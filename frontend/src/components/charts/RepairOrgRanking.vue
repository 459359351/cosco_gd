<template>
  <div class="org-ranking">
    <div class="ranking-header">
      <div class="switch-btns">
        <button :class="{ active: tab === 'self' }" @click="switchTab('self')">自营网点</button>
        <button :class="{ active: tab === 'outsourced' }" @click="switchTab('outsourced')">外包网点</button>
      </div>
    </div>
    <div class="ranking-body" ref="bodyRef">
      <div
        v-for="(item, idx) in currentList"
        :key="item.org_code"
        class="ranking-row"
        :class="{ selected: store.selectedParent === item.org_name, highlight: autoIdx === idx }"
        @click="manualSelect(idx)"
      >
        <span class="rank" :class="{ top3: idx < 3 }">{{ idx + 1 }}</span>
        <span class="name">{{ item.org_name }}</span>
        <span class="bar-wrap">
          <span class="bar" :style="{ width: barWidth(item.revenue) + '%' }" />
        </span>
        <span class="value">{{ formatWan(item.revenue) }}万</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();
const tab = ref<"self" | "outsourced">("self");
const bodyRef = ref<HTMLElement | null>(null);
const autoIdx = ref(0);
const CAROUSEL_INTERVAL = 8000;
let carouselTimer: ReturnType<typeof setInterval> | null = null;
let pauseTimer: ReturnType<typeof setTimeout> | null = null;

const currentList = computed(() =>
  tab.value === "self" ? store.selfOrgs : store.outsourcedOrgs,
);

const maxRev = computed(() => {
  const list = currentList.value;
  if (!list.length) return 1;
  return Math.max(...list.map((i) => i.revenue)) || 1;
});

function barWidth(rev: number) {
  return (rev / maxRev.value) * 100;
}

function formatWan(n: number) {
  return (n / 10000).toFixed(1);
}

async function autoNext() {
  const list = currentList.value;
  if (!list.length) return;
  autoIdx.value = (autoIdx.value + 1) % list.length;
  const item = list[autoIdx.value];
  if (!item) return;
  /* 只在钻取视图时触发地图 drilldown，聚合视图仅高亮行 */
  if (store.viewMode === "drilldown") {
    await store.drilldown(item.org_name);
  }
}

function startCarousel() {
  stopCarousel();
  carouselTimer = setInterval(autoNext, CAROUSEL_INTERVAL);
}

function stopCarousel() {
  if (carouselTimer) {
    clearInterval(carouselTimer);
    carouselTimer = null;
  }
}

function manualSelect(idx: number) {
  autoIdx.value = idx;
  const item = currentList.value[idx];
  if (item) store.drilldown(item.org_name);
  // 暂停自动轮播，10秒后恢复
  stopCarousel();
  if (pauseTimer) clearTimeout(pauseTimer);
  pauseTimer = setTimeout(startCarousel, 10000);
}

function switchTab(t: "self" | "outsourced") {
  tab.value = t;
  autoIdx.value = 0;
}

onMounted(() => {
  startCarousel();
});

onBeforeUnmount(() => {
  stopCarousel();
  if (pauseTimer) clearTimeout(pauseTimer);
});
</script>

<style scoped lang="scss">
.org-ranking {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
}
.ranking-header {
  margin-bottom: 6px;
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
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.3s;
  &:hover {
    background: rgba(0, 212, 255, 0.08);
  }
  &.selected {
    background: rgba(0, 212, 255, 0.15);
  }
  &.highlight {
    animation: row-pulse 0.6s ease;
  }
}
@keyframes row-pulse {
  0% { background: rgba(0, 212, 255, 0.4); }
  100% { background: rgba(0, 212, 255, 0.15); }
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
  width: 90px;
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
  width: 60px;
  text-align: right;
  font-size: 12px;
  color: #e0f0ff;
}
</style>
