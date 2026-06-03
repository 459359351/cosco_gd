<template>
  <div class="kpi-cards">
    <!-- 需求5-1: 修箱收入 / 箱量 / 单箱收入 -->
    <div class="kpi-card" style="border-left-color: #00d4ff">
      <div class="kpi-title" style="color: #00d4ff">修箱收入</div>
      <div class="kpi-row">
        <div class="kpi-metric">
          <span class="kpi-value">{{ formatWan(totalRevenue) }}</span>
          <span class="kpi-unit">万元</span>
        </div>
      </div>
      <div class="kpi-sub kpi-sub-col">
        <span>箱量 {{ formatNum(totalQty) }} 个</span>
        <span>单箱 ¥{{ formatNum(unitPrice) }}</span>
      </div>
      <div class="kpi-trend" :class="revWowClass">
        {{ revWowArrow }} {{ formatPct(revWow) }} 环比
      </div>
    </div>

    <!-- 需求5-2: 本周总收入 -->
    <div class="kpi-card highlight" style="border-left-color: #2ecc71">
      <div class="kpi-title" style="color: #2ecc71">本周总收入</div>
      <div class="kpi-row">
        <div class="kpi-metric">
          <span class="kpi-value" style="color: #2ecc71">{{ formatWan(totalRevenue) }}</span>
          <span class="kpi-unit">万元</span>
        </div>
      </div>
      <div class="kpi-sub">
        <span>上周 {{ formatWan(lastWeekRevenue) }} 万元</span>
      </div>
      <div class="kpi-trend" :class="revWowClass">
        {{ revWowArrow }} {{ formatPct(revWow) }} 环比变动
      </div>
    </div>

    <!-- 需求5-3: 中远海 -->
    <div class="kpi-card" style="border-left-color: #00d4ff">
      <div class="kpi-title" style="color: #00d4ff">中远海 COSCO</div>
      <div class="kpi-inline">
        <span class="kpi-label">收入</span>
        <span class="kpi-value-sm">{{ formatWan(coscoRev) }}<span class="kpi-unit">万</span></span>
        <span v-if="coscoRevWow !== null" class="kpi-change" :class="coscoRevWow > 0 ? 'up' : 'down'">
          {{ coscoRevWow > 0 ? '↑' : '↓' }}{{ formatPct(coscoRevWow) }}
        </span>
      </div>
      <div class="kpi-inline">
        <span class="kpi-label">箱量</span>
        <span class="kpi-value-sm">{{ formatNum(coscoQty) }}<span class="kpi-unit">个</span></span>
      </div>
      <div class="kpi-inline">
        <span class="kpi-label">单箱</span>
        <span class="kpi-value-sm">¥{{ formatNum(coscoUnit) }}</span>
      </div>
    </div>

    <!-- 需求5-3: 第三方 -->
    <div class="kpi-card" style="border-left-color: #ff9f43">
      <div class="kpi-title" style="color: #ff9f43">第三方客户</div>
      <div class="kpi-inline">
        <span class="kpi-label">收入</span>
        <span class="kpi-value-sm">{{ formatWan(thirdRev) }}<span class="kpi-unit">万</span></span>
        <span v-if="thirdRevWow !== null" class="kpi-change" :class="thirdRevWow > 0 ? 'up' : 'down'">
          {{ thirdRevWow > 0 ? '↑' : '↓' }}{{ formatPct(thirdRevWow) }}
        </span>
      </div>
      <div class="kpi-inline">
        <span class="kpi-label">箱量</span>
        <span class="kpi-value-sm">{{ formatNum(thirdQty) }}<span class="kpi-unit">个</span></span>
      </div>
      <div class="kpi-inline">
        <span class="kpi-label">单箱</span>
        <span class="kpi-value-sm">¥{{ formatNum(thirdUnit) }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRepairStore } from "@/store/repair";

const store = useRepairStore();

const totalRevenue = computed(() => store.kpi?.total?.revenue ?? 0);
const totalQty = computed(() => store.kpi?.total?.container_qty ?? 0);
const unitPrice = computed(() => store.kpi?.total?.unit_price ?? 0);
const revWow = computed(() => store.kpi?.total?.rev_wow ?? 0);

const coscoRev = computed(() => store.kpi?.cosco?.revenue ?? 0);
const coscoQty = computed(() => store.kpi?.cosco?.container_qty ?? 0);
const coscoUnit = computed(() => store.kpi?.cosco?.unit_price ?? 0);
const coscoRevWow = computed(() => store.kpi?.cosco?.rev_wow ?? null);

const thirdRev = computed(() => store.kpi?.thirdparty?.revenue ?? 0);
const thirdQty = computed(() => store.kpi?.thirdparty?.container_qty ?? 0);
const thirdUnit = computed(() => store.kpi?.thirdparty?.unit_price ?? 0);
const thirdRevWow = computed(() => store.kpi?.thirdparty?.rev_wow ?? null);

const lastWeekRevenue = computed(() => {
  const tr = totalRevenue.value;
  const rw = revWow.value;
  if (!tr || !rw) return 0;
  return tr / (1 + rw);
});

const revWowClass = computed(() => revWow.value > 0 ? 'up' : 'down');
const revWowArrow = computed(() => revWow.value > 0 ? '↑' : '↓');

function formatNum(n: number) {
  if (!n) return "0";
  return n.toLocaleString();
}
function formatWan(n: number) {
  if (!n) return "0.00";
  return (n / 10000).toFixed(2);
}
function formatPct(n: number) {
  if (n === null || n === undefined) return "0%";
  return (n > 0 ? "+" : "") + (n * 100).toFixed(2) + "%";
}
</script>

<style scoped lang="scss">
.kpi-cards {
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: max(6px, 0.6vh) max(6px, 0.5vw);
  padding: max(6px, 0.6vh) max(8px, 0.5vw);
  height: 100%;
  overflow: hidden;
}
.kpi-card {
  padding: max(6px, 0.7vh) max(8px, 0.6vw);
  border: 1px solid rgba(57, 216, 255, 0.25);
  border-left: 3px solid;
  background: linear-gradient(180deg, rgba(8, 28, 56, 0.88), rgba(4, 14, 28, 0.88));
  border-radius: max(6px, 0.4vw);
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-height: 0;
  overflow: hidden;
}
.kpi-card:hover {
  border-color: rgba(57, 216, 255, 0.5);
  box-shadow: 0 0 15px rgba(0, 212, 255, 0.1);
}
.kpi-card.highlight {
  background: linear-gradient(180deg, rgba(8, 40, 30, 0.9), rgba(4, 20, 14, 0.9));
  border: 1px solid rgba(46, 204, 113, 0.3);
}
.kpi-title {
  font-size: clamp(10px, 0.75vw, 13px);
  font-weight: 600;
  margin-bottom: max(2px, 0.3vh);
  letter-spacing: 1px;
}
.kpi-row {
  display: flex;
  gap: max(6px, 0.6vw);
}
.kpi-metric {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 4px;
  flex-wrap: wrap;
}
.kpi-sep {
  width: 8px;
  flex-shrink: 0;
}
.kpi-label {
  color: rgba(168, 201, 255, 0.7);
  font-size: clamp(9px, 0.6vw, 12px);
}
.kpi-value {
  font-size: clamp(14px, 1.2vw, 20px);
  font-weight: 700;
  color: #e0f0ff;
  line-height: 1.2;
  white-space: nowrap;
}
.kpi-unit {
  font-size: clamp(9px, 0.6vw, 12px);
  color: rgba(168, 201, 255, 0.5);
}
.kpi-inline {
  display: flex;
  align-items: baseline;
  gap: 4px;
  white-space: nowrap;
}
.kpi-value-sm {
  font-size: clamp(12px, 1vw, 16px);
  font-weight: 700;
  color: #e0f0ff;
  line-height: 1.3;
}
.kpi-sub {
  display: flex;
  gap: 10px;
  margin-top: max(2px, 0.3vh);
  font-size: clamp(9px, 0.6vw, 12px);
  color: rgba(168, 201, 255, 0.6);
}
.kpi-sub-col {
  flex-direction: column;
  gap: 1px;
}
.kpi-trend {
  font-size: clamp(10px, 0.7vw, 13px);
  margin-top: max(2px, 0.3vh);
  font-weight: 600;
}
.kpi-trend.up {
  color: #2ecc71;
}
.kpi-trend.down {
  color: #e74c3c;
}
.kpi-change {
  font-size: clamp(9px, 0.6vw, 12px);
  margin-left: 4px;
}
.kpi-change.up {
  color: #2ecc71;
}
.kpi-change.down {
  color: #e74c3c;
}
</style>
