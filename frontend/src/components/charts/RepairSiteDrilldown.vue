<template>
  <div class="drilldown">
    <template v-if="!store.selectedParent">
      <div class="empty">点击左侧排名选择运营中心或外包商</div>
    </template>
    <template v-else>
      <div class="drilldown-title">
        {{ store.selectedParent }} — 下属网点明细
        <button class="back-btn" @click="clearDrilldown">返回</button>
      </div>
      <div class="site-list">
        <div v-for="item in store.siteDetails" :key="item.site_name" class="site-row">
          <span class="site-name">{{ item.site_name }}</span>
          <span class="site-bar-wrap">
            <span class="site-bar" :style="{ width: item.pct + '%' }" />
          </span>
          <span class="site-value">{{ formatWan(item.approved_amount) }}万</span>
          <span class="site-pct">{{ item.pct }}%</span>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useRepairStore } from "@/store/repair";

const store = useRepairStore();

function clearDrilldown() {
  store.selectedParent = null;
  store.siteDetails = [];
}

function formatWan(n: number) {
  return (n / 10000).toFixed(2);
}
</script>

<style scoped lang="scss">
.drilldown {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 8px 12px;
}
.empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: rgba(168, 201, 255, 0.4);
  font-size: 13px;
}
.drilldown-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 13px;
  color: #00d4ff;
  margin-bottom: 8px;
}
.back-btn {
  font-size: 11px;
  padding: 2px 8px;
  border: 1px solid rgba(57, 216, 255, 0.3);
  background: transparent;
  color: rgba(168, 201, 255, 0.7);
  border-radius: 3px;
  cursor: pointer;
}
.site-list {
  flex: 1;
  overflow: auto;
}
.site-row {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 2px;
}
.site-name {
  width: 100px;
  font-size: 12px;
  color: #a7fbff;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.site-bar-wrap {
  flex: 1;
  height: 6px;
  background: rgba(57, 216, 255, 0.08);
  border-radius: 3px;
  overflow: hidden;
}
.site-bar {
  display: block;
  height: 100%;
  background: linear-gradient(90deg, #2ecc71, #27ae60);
  border-radius: 3px;
}
.site-value {
  width: 60px;
  text-align: right;
  font-size: 11px;
  color: #e0f0ff;
}
.site-pct {
  width: 40px;
  text-align: right;
  font-size: 11px;
  color: rgba(168, 201, 255, 0.6);
}
</style>
