<template>
  <div
    class="preview-popup"
    :style="style"
  >
    <!-- 顶部: 周标签 -->
    <div class="preview-header">
      <span class="preview-week">{{ week.week_label }}</span>
      <span class="preview-range">{{ week.date_range }}</span>
    </div>

    <!-- 3 个 block 卡片 -->
    <div class="preview-blocks">
      <!-- 中远海 -->
      <div
        class="preview-block"
        style="border-left-color: #00d4ff"
      >
        <div
          class="block-title"
          style="color: #00d4ff"
        >
          中远海
        </div>
        <div class="block-row">
          <span class="block-label">收入</span>
          <span class="block-value">{{ formatWan(cosco?.revenue ?? 0) }}<span class="block-unit">万</span></span>
        </div>
        <div class="block-row">
          <span class="block-label">箱量</span>
          <span class="block-value">{{ formatNum(cosco?.container_qty ?? 0) }}</span>
        </div>
        <div class="block-row">
          <span class="block-label">环比</span>
          <span
            class="block-change"
            :class="cosco?.rev_wow > 0 ? 'up' : 'down'"
          >
            {{ cosco?.rev_wow > 0 ? "↑" : "↓" }}{{ formatPct(cosco?.rev_wow ?? 0) }}
          </span>
        </div>
      </div>

      <!-- 第三方 -->
      <div
        class="preview-block"
        style="border-left-color: #ff9f43"
      >
        <div
          class="block-title"
          style="color: #ff9f43"
        >
          第三方
        </div>
        <div class="block-row">
          <span class="block-label">收入</span>
          <span class="block-value">{{ formatWan(third?.revenue ?? 0) }}<span class="block-unit">万</span></span>
        </div>
        <div class="block-row">
          <span class="block-label">箱量</span>
          <span class="block-value">{{ formatNum(third?.container_qty ?? 0) }}</span>
        </div>
        <div class="block-row">
          <span class="block-label">环比</span>
          <span
            class="block-change"
            :class="third?.rev_wow > 0 ? 'up' : 'down'"
          >
            {{ third?.rev_wow > 0 ? "↑" : "↓" }}{{ formatPct(third?.rev_wow ?? 0) }}
          </span>
        </div>
      </div>

      <!-- 合计 -->
      <div
        class="preview-block"
        style="border-left-color: #2ecc71"
      >
        <div
          class="block-title"
          style="color: #2ecc71"
        >
          合计
        </div>
        <div class="block-row">
          <span class="block-label">收入</span>
          <span class="block-value">{{ formatWan(total?.revenue ?? 0) }}<span class="block-unit">万</span></span>
        </div>
        <div class="block-row">
          <span class="block-label">箱量</span>
          <span class="block-value">{{ formatNum(total?.container_qty ?? 0) }}</span>
        </div>
        <div class="block-row">
          <span class="block-label">单箱</span>
          <span class="block-value">¥{{ formatNum(total?.unit_price ?? 0) }}</span>
        </div>
        <div class="block-row">
          <span class="block-label">环比</span>
          <span
            class="block-change"
            :class="total?.rev_wow > 0 ? 'up' : 'down'"
          >
            {{ total?.rev_wow > 0 ? "↑" : "↓" }}{{ formatPct(total?.rev_wow ?? 0) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import type { AvailableWeekItem } from "@/api/repairDashboard";
import type { RepairKpiBlock } from "@/store/repair";

interface KpiOverview {
  self_: RepairKpiBlock;
  outsourced: RepairKpiBlock;
  thirdparty: RepairKpiBlock;
  cosco: RepairKpiBlock;
  total: RepairKpiBlock;
  week_label: string;
}

const props = defineProps<{
  data: KpiOverview | null;
  week: AvailableWeekItem;
  top?: number;
}>();

const style = computed(() => ({
  top: `${props.top ?? 0}px`,
}));

const cosco = computed(() => props.data?.cosco ?? null);
const third = computed(() => props.data?.thirdparty ?? null);
const total = computed(() => props.data?.total ?? null);

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
.preview-popup {
  position: absolute;
  left: 100%;
  margin-left: max(8px, 0.42vw);
  width: clamp(260px, 18vw, 360px);
  background: linear-gradient(180deg, rgba(8, 28, 56, 0.96), rgba(4, 14, 28, 0.96));
  border: 1px solid rgba(57, 216, 255, 0.4);
  border-radius: max(6px, 0.4vw);
  box-shadow: 0 0 20px rgba(0, 212, 255, 0.15), inset 0 0 30px rgba(26, 174, 255, 0.08);
  padding: max(8px, 0.6vh) max(10px, 0.5vw);
  z-index: 5001;
  pointer-events: none;
}

.preview-header {
  display: flex;
  align-items: baseline;
  gap: max(6px, 0.42vw);
  margin-bottom: max(6px, 0.5vh);
  padding-bottom: max(4px, 0.3vh);
  border-bottom: 1px solid rgba(57, 216, 255, 0.2);
}

.preview-week {
  font-size: clamp(12px, 0.9vw, 15px);
  font-weight: 700;
  color: #7ee7ff;
}

.preview-range {
  font-size: clamp(10px, 0.65vw, 12px);
  color: rgba(168, 201, 255, 0.6);
}

.preview-blocks {
  display: flex;
  gap: max(6px, 0.4vw);
}

.preview-block {
  flex: 1;
  padding: max(4px, 0.4vh) max(6px, 0.4vw);
  border: 1px solid rgba(57, 216, 255, 0.2);
  border-left: 2px solid;
  border-radius: max(4px, 0.25vw);
  background: rgba(8, 28, 56, 0.5);
}

.block-title {
  font-size: clamp(9px, 0.6vw, 11px);
  font-weight: 600;
  margin-bottom: max(2px, 0.2vh);
}

.block-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 2px;
  white-space: nowrap;
}

.block-label {
  font-size: clamp(8px, 0.5vw, 10px);
  color: rgba(168, 201, 255, 0.6);
}

.block-value {
  font-size: clamp(10px, 0.7vw, 13px);
  font-weight: 700;
  color: #e0f0ff;
}

.block-unit {
  font-size: clamp(8px, 0.5vw, 10px);
  color: rgba(168, 201, 255, 0.5);
}

.block-change {
  font-size: clamp(9px, 0.55vw, 11px);
  font-weight: 600;
}

.block-change.up {
  color: #2ecc71;
}

.block-change.down {
  color: #e74c3c;
}
</style>
