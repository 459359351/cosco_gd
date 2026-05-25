<template>
  <div class="org-ranking">
    <div class="ranking-header">
      <div class="switch-btns">
        <button :class="{ active: tab === 'self' }" @click="tab = 'self'">自营网点</button>
        <button :class="{ active: tab === 'outsourced' }" @click="tab = 'outsourced'">外包网点</button>
      </div>
    </div>
    <div class="ranking-body">
      <div
        v-for="(item, idx) in currentList"
        :key="item.org_code"
        class="ranking-row"
        :class="{ selected: store.selectedParent === item.org_name }"
        @click="store.drilldown(item.org_name)"
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
import { computed, ref } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();
const tab = ref<"self" | "outsourced">("self");

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
</script>

<style scoped lang="scss">
.org-ranking {
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
}
.ranking-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 5px 4px;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.2s;
  &:hover {
    background: rgba(0, 212, 255, 0.08);
  }
  &.selected {
    background: rgba(0, 212, 255, 0.15);
  }
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
