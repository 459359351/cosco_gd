<template>
  <div class="kpi-cards">
    <div v-for="block in blocks" :key="block.key" class="kpi-card" :style="{ borderColor: block.color }">
      <div class="kpi-title" :style="{ color: block.color }">{{ block.label }}</div>
      <div class="kpi-row">
        <div class="kpi-metric">
          <span class="kpi-label">修理量</span>
          <span class="kpi-value">{{ formatNum(block.qty) }}</span>
          <span class="kpi-unit">箱</span>
          <span v-if="block.qtyWow" class="kpi-change" :class="block.qtyWow > 0 ? 'up' : 'down'">
            {{ block.qtyWow > 0 ? '↑' : '↓' }} 环比 +{{ formatNum(block.qtyWow) }} 箱
          </span>
        </div>
        <div class="kpi-metric">
          <span class="kpi-label">修理收入</span>
          <span class="kpi-value">{{ formatWan(block.rev) }}</span>
          <span class="kpi-unit">万</span>
          <span v-if="block.revWow" class="kpi-change" :class="block.revWow > 0 ? 'up' : 'down'">
            {{ block.revWow > 0 ? '↑' : '↓' }} 环比 {{ formatPct(block.revWow) }}
          </span>
        </div>
      </div>
      <div v-if="block.qtyYoy !== null" class="kpi-yoy">
        同比 {{ block.qtyYoy >= 0 ? '+' : '' }}{{ block.qtyYoy?.toLocaleString() }} 箱
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();

const blocks = computed(() => {
  const kpi = store.kpi;
  if (!kpi) return [];

  return [
    {
      key: "self",
      label: "自营",
      color: "#00d4ff",
      qty: kpi.self_.container_qty,
      qtyWow: kpi.self_.qty_wow,
      rev: kpi.self_.revenue,
      revWow: kpi.self_.rev_wow,
      qtyYoy: kpi.self_.qty_yoy,
    },
    {
      key: "outsourced",
      label: "外包",
      color: "#ff9f43",
      qty: kpi.outsourced.container_qty,
      qtyWow: kpi.outsourced.qty_wow,
      rev: kpi.outsourced.revenue,
      revWow: kpi.outsourced.rev_wow,
      qtyYoy: kpi.outsourced.qty_yoy,
    },
    {
      key: "thirdparty",
      label: "第三方干箱",
      color: "#2ecc71",
      qty: kpi.thirdparty.container_qty,
      qtyWow: kpi.thirdparty.qty_wow,
      rev: kpi.thirdparty.revenue,
      revWow: kpi.thirdparty.rev_wow,
      qtyYoy: kpi.thirdparty.qty_yoy,
    },
  ];
});

function formatNum(n: number) {
  return n?.toLocaleString() ?? "0";
}
function formatWan(n: number) {
  return (n / 10000).toFixed(2);
}
function formatPct(n: number) {
  if (!n) return "0%";
  return (n > 0 ? "+" : "") + (n * 100).toFixed(0) + "%";
}
</script>

<style scoped lang="scss">
.kpi-cards {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 10px;
  height: 100%;
  overflow: auto;
}
.kpi-card {
  padding: 10px 12px;
  border: 1px solid rgba(57, 216, 255, 0.35);
  border-left: 3px solid;
  background: linear-gradient(180deg, rgba(8, 28, 56, 0.88), rgba(4, 14, 28, 0.88));
  border-radius: 6px;
}
.kpi-title {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
}
.kpi-row {
  display: flex;
  gap: 16px;
}
.kpi-metric {
  flex: 1;
}
.kpi-label {
  color: rgba(168, 201, 255, 0.7);
  font-size: 11px;
}
.kpi-value {
  font-size: 20px;
  font-weight: 700;
  color: #e0f0ff;
  margin: 0 4px;
}
.kpi-unit {
  color: rgba(168, 201, 255, 0.5);
  font-size: 11px;
}
.kpi-change {
  font-size: 11px;
  margin-left: 6px;
  &.up {
    color: #2ecc71;
  }
  &.down {
    color: #e74c3c;
  }
}
.kpi-yoy {
  margin-top: 4px;
  font-size: 11px;
  color: rgba(168, 201, 255, 0.6);
}
</style>
