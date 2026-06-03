<template>
  <ScreenLayout>
    <template #left-top>
      <div class="slot-col">
        <PanelTitle title="核心经营指标" />
        <div class="slot-body"><RepairKpiCards /></div>
      </div>
    </template>

    <template #left-mid>
      <div class="slot-col">
        <PanelTitle title="客户类型占比" />
        <div class="slot-body pie-slot"><CustomerPieChart /></div>
      </div>
    </template>

    <template #left-bottom></template>

    <template #center>
      <div v-if="showAdmin" class="toolbar">
        <el-button class="console-link" type="primary" link @click="goAdmin">系统管理</el-button>
        <el-button class="console-link" type="primary" link @click="goDataConsole">数据管理</el-button>
      </div>
      <MapCore />
    </template>

    <template #right-top>
      <div class="slot-col">
        <PanelTitle title="自营/外包网点排名" />
        <div class="slot-body"><RepairOrgRanking /></div>
      </div>
    </template>

    <template #right-bottom>
      <div class="slot-col">
        <PanelTitle title="网点明细" />
        <div class="slot-body"><RepairSiteDrilldown /></div>
      </div>
    </template>

    <template #footer>
      <div class="footer-left">
        <div class="slot-col">
          <PanelTitle title="累计修理排名" />
          <div class="slot-body"><CumulativeRankChart /></div>
        </div>
      </div>
      <div class="footer-right">
        <div class="cockpit-footer-inner">
          <PanelTitle title="修理业务机构排名" />
          <div class="cockpit-footer-table">
            <RepairOrgTable />
          </div>
        </div>
      </div>
    </template>
  </ScreenLayout>
</template>

<script setup lang="ts">
import { ElButton } from "element-plus";
import { computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";

import CustomerPieChart from "@/components/charts/CustomerPieChart.vue";
import RepairOrgRanking from "@/components/charts/RepairOrgRanking.vue";
import RepairSiteDrilldown from "@/components/charts/RepairSiteDrilldown.vue";
import PanelTitle from "@/components/decorations/PanelTitle.vue";
import MapCore from "@/components/map/MapCore.vue";
import RepairKpiCards from "@/components/kpi/RepairKpiCards.vue";
import CumulativeRankChart from "@/components/charts/CumulativeRankChart.vue";
import RepairOrgTable from "@/components/tables/RepairOrgTable.vue";
import ScreenLayout from "@/layouts/ScreenLayout.vue";
import { useRepairStore } from "@/store/repair";

const repairStore = useRepairStore();
const router = useRouter();
const route = useRoute();

const showAdmin = computed(() => route.query.admin === "true");

function goAdmin() {
  void router.push("/admin");
}

function goDataConsole() {
  void router.push("/data-console");
}

onMounted(() => {
  repairStore.loadAll();
});
</script>

<style scoped lang="scss">
/* 驾驶舱全屏容器，移除 scale 方案，由 ScreenLayout 弹性布局接管 */
.toolbar {
  position: absolute;
  top: max(6px, 0.93vh);
  left: max(6px, 0.52vw);
  z-index: 5000;
  pointer-events: auto;
}
.console-link {
  margin-left: max(4px, 0.42vw);
  color: rgba(180, 220, 255, 0.95) !important;
  font-size: clamp(12px, 0.73vw, 15px);
}

/* 底部栏：标题固定高度，表格占剩余空间并内部滚动 */
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

.footer-left,
.footer-right {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 左侧/右侧面板通用弹性容器 */
.slot-col {
  display: flex;
  flex-direction: column;
  height: 100%;
}
.slot-body {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}
.pie-slot {
  overflow: visible;
}
</style>
