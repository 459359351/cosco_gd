<template>
  <el-table :data="store.alerts" height="100%" @row-click="onRowClick">
    <el-table-column prop="created_at" label="时间" min-width="140" />
    <el-table-column prop="alert_type" label="类型" min-width="90" />
    <el-table-column prop="message" label="内容" />
  </el-table>
</template>

<script setup lang="ts">
import { ElTable, ElTableColumn } from "element-plus";

import { useSelectionStore } from "@/store/selection";
import { useYardStore } from "@/store/yard";

const store = useYardStore();
const selection = useSelectionStore();

const onRowClick = (row: any) => {
  selection.focusYard(row.yard_id);
};
</script>
