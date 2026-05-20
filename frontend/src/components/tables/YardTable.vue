<template>
  <el-table
    :data="store.rankingItems"
    class="cockpit-yard-table"
    height="100%"
    row-key="id"
    highlight-current-row
    @row-click="onRowClick"
  >
    <el-table-column prop="name" label="点位" min-width="200" />
    <el-table-column prop="province" label="省份" width="90" />
    <el-table-column prop="capacity" label="容量" width="120" />
    <el-table-column prop="status" label="状态" width="100" />
  </el-table>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from "element-plus";

import { useSelectionStore } from "@/store/selection";
import { useYardStore } from "@/store/yard";

const store = useYardStore();
const selection = useSelectionStore();

const onRowClick = (row: any) => {
  selection.focusYard(row.id);
};
</script>

<style scoped lang="scss">
.cockpit-yard-table {
  --el-table-bg-color: transparent;
  --el-table-tr-bg-color: rgba(6, 26, 52, 0.55);
  --el-table-header-bg-color: rgba(8, 36, 68, 0.92);
  --el-table-row-hover-bg-color: rgba(26, 130, 200, 0.28);
  --el-table-current-row-bg-color: rgba(44, 160, 230, 0.32);
  --el-table-border-color: rgba(57, 216, 255, 0.22);
  --el-table-text-color: #c8ebff;
  --el-table-header-text-color: #8ae8ff;
  background: transparent;
}

.cockpit-yard-table :deep(.el-table__inner-wrapper::before) {
  display: none;
}

.cockpit-yard-table :deep(th.el-table__cell) {
  font-weight: 600;
  letter-spacing: 0.5px;
}

.cockpit-yard-table :deep(td.el-table__cell) {
  padding: 8px 10px;
}

.cockpit-yard-table :deep(.cell) {
  line-height: 1.4;
}

.cockpit-yard-table :deep(.el-table__body tr) {
  cursor: pointer;
}

.cockpit-yard-table :deep(.el-table__empty-text) {
  color: rgba(138, 232, 255, 0.55);
}
</style>
