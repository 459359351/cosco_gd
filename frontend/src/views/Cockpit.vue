<template>
  <div class="screen-stage">
    <div class="screen-scale" :style="{ transform: `scale(${scale})` }">
      <ScreenLayout>
        <template #left-top>
          <div class="slot-col">
            <PanelTitle title="每周修理量与修理收入" />
            <div class="slot-body"><RepairKpiCards /></div>
          </div>
        </template>

        <template #left-mid>
          <div class="slot-col">
            <PanelTitle title="客户类型占比" />
            <div class="slot-body"><CustomerPieChart /></div>
          </div>
        </template>

        <template #left-bottom>
          <div class="slot-col">
            <PanelTitle title="累计修理排名" />
            <div class="slot-body"><CumulativeRankChart /></div>
          </div>
        </template>

        <template #center>
          <div v-if="showAdmin" class="toolbar">
            <el-button class="console-link" type="primary" link @click="goAdmin">系统管理</el-button>
            <el-button class="console-link" type="primary" link @click="goAdmin">数据管理</el-button>
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
          <div class="cockpit-footer-inner">
            <PanelTitle title="修理业务机构排名" />
            <div class="cockpit-footer-table">
              <RepairOrgTable />
            </div>
          </div>
        </template>
      </ScreenLayout>
    </div>
  </div>
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
import { useScreenAdapter } from "@/composables/useScreenAdapter";
import ScreenLayout from "@/layouts/ScreenLayout.vue";
import { useRepairStore } from "@/store/repair";

const { scale } = useScreenAdapter();
const repairStore = useRepairStore();
const router = useRouter();
const route = useRoute();

const showAdmin = computed(() => route.query.admin === "true");

function goAdmin() {
  void router.push("/admin");
}

onMounted(() => {
  repairStore.loadAll();
});
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
</style>
