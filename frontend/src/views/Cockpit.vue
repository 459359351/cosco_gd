<template>
  <div class="screen-stage">
    <div class="screen-scale" :style="{ transform: `scale(${scale})` }">
      <ScreenLayout>
        <template #left-top>
          <PanelTitle title="关键指标" />
          <KpiCards />
        </template>

        <template #left-mid>
          <PanelTitle title="点位容量排名" />
          <RankingBarChart />
        </template>

        <template #left-bottom>
          <PanelTitle title="7日吞吐趋势" />
          <TrendLineChart />
        </template>

        <template #center>
          <div class="toolbar">
            <el-select
              v-model="selection.province"
              class="province-select"
              placeholder="筛选省份"
              clearable
              teleported
              popper-class="cockpit-province-popper"
            >
              <el-option label="广东" value="广东" />
              <el-option label="广西" value="广西" />
            </el-select>
            <el-button class="console-link" type="primary" link @click="goDataConsole">
              数据管理
            </el-button>
          </div>
          <MapCore />
          <YardDrawer />
        </template>

        <template #right-top>
          <PanelTitle title="货种结构分布" />
          <CargoPieChart />
        </template>

        <template #right-mid>
          <PanelTitle title="堆场状态占比" />
          <StatusGaugeChart />
        </template>

        <template #right-bottom>
          <PanelTitle title="实时预警" />
          <AlertScrollBoard />
        </template>

        <template #footer>
          <div class="cockpit-footer-inner">
            <PanelTitle title="TOP10 物流点位明细" />
            <div class="cockpit-footer-table">
              <YardTable />
            </div>
          </div>
        </template>
      </ScreenLayout>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElButton, ElOption, ElSelect } from "element-plus";
import { onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";

import CargoPieChart from "@/components/charts/CargoPieChart.vue";
import RankingBarChart from "@/components/charts/RankingBarChart.vue";
import StatusGaugeChart from "@/components/charts/StatusGaugeChart.vue";
import TrendLineChart from "@/components/charts/TrendLineChart.vue";
import PanelTitle from "@/components/decorations/PanelTitle.vue";
import MapCore from "@/components/map/MapCore.vue";
import YardDrawer from "@/components/map/YardDrawer.vue";
import KpiCards from "@/components/kpi/KpiCards.vue";
import AlertScrollBoard from "@/components/tables/AlertScrollBoard.vue";
import YardTable from "@/components/tables/YardTable.vue";
import { useScreenAdapter } from "@/composables/useScreenAdapter";
import { useWS } from "@/composables/useWS";
import ScreenLayout from "@/layouts/ScreenLayout.vue";
import { useSelectionStore } from "@/store/selection";
import { useYardStore } from "@/store/yard";

const { scale } = useScreenAdapter();
const store = useYardStore();
const selection = useSelectionStore();
const router = useRouter();

function goDataConsole() {
  void router.push({ name: "DataConsole" });
}

useWS();

onMounted(() => {
  store.loadAll();
});

let idleTimer: number | null = null;
let idleRound = 0;
const idleEvents = ["mousemove", "keydown", "wheel"];
const resetIdlePatrol = () => {
  if (idleTimer) window.clearInterval(idleTimer);
  idleTimer = window.setInterval(() => {
    if (!store.rankingItems.length) return;
    const target = store.rankingItems[idleRound % store.rankingItems.length];
    selection.focusYard(target.id);
    idleRound += 1;
  }, 5000);
};

const bindIdlePatrol = () => {
  idleEvents.forEach((eventName) => {
    window.addEventListener(eventName, resetIdlePatrol);
  });
  resetIdlePatrol();
};

onMounted(bindIdlePatrol);
onUnmounted(() => {
  if (idleTimer) window.clearInterval(idleTimer);
  idleEvents.forEach((eventName) => {
    window.removeEventListener(eventName, resetIdlePatrol);
  });
});

watch(
  () => selection.province,
  (val) => {
    selection.focusYard(null);
    store.loadAll(val);
  },
);
</script>

<style scoped lang="scss">
.screen-stage {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  background:
    radial-gradient(circle at 30% 20%, rgba(60, 185, 255, 0.18), transparent 40%),
    radial-gradient(circle at 70% 80%, rgba(37, 125, 220, 0.22), transparent 45%),
    #050d1f;
}
.screen-scale {
  width: 1920px;
  height: 1080px;
  transform-origin: left top;
}
.toolbar {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 5000;
  pointer-events: auto;
}
.province-select {
  width: 140px;
}
.console-link {
  margin-left: 8px;
  color: rgba(180, 220, 255, 0.95) !important;
  font-size: 14px;
}

/* 底部栏：标题固定高度，表格占剩余空间并内部滚动，避免最后一行被 panel overflow 裁切 */
.cockpit-footer-inner {
  box-sizing: border-box;
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}
.cockpit-footer-table {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
</style>
