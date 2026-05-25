<template>
  <div class="org-table">
    <el-table :data="allOrgs" size="small" max-height="200" @row-click="onRowClick">
      <el-table-column prop="org_name" label="名称" min-width="120" show-overflow-tooltip />
      <el-table-column prop="company_type" label="类型" width="60">
        <template #default="{ row }">
          <span :class="row.company_type === 'self' ? 'type-self' : 'type-out'">
            {{ row.company_type === "self" ? "自营" : "外包" }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="container_qty" label="箱量" width="80">
        <template #default="{ row }">{{ row.container_qty?.toLocaleString() }}</template>
      </el-table-column>
      <el-table-column prop="revenue" label="收入(万)" width="80">
        <template #default="{ row }">{{ (row.revenue / 10000).toFixed(1) }}</template>
      </el-table-column>
      <el-table-column prop="qty_wow" label="环比" width="60">
        <template #default="{ row }">
          <span :class="row.qty_wow > 0 ? 'up' : row.qty_wow < 0 ? 'down' : ''">
            {{ row.qty_wow > 0 ? "+" : "" }}{{ row.qty_wow }}
          </span>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();

const allOrgs = computed(() => {
  return [...store.selfOrgs, ...store.outsourcedOrgs].sort((a, b) => b.revenue - a.revenue);
});

function onRowClick(row: any) {
  store.drilldown(row.org_name);
}
</script>

<style scoped lang="scss">
.org-table {
  height: 100%;
  padding: 0 8px;
  :deep(.el-table) {
    --el-table-bg-color: transparent;
    --el-table-tr-bg-color: transparent;
    --el-table-header-bg-color: rgba(13, 43, 79, 0.5);
    --el-table-row-hover-bg-color: rgba(0, 212, 255, 0.08);
    --el-table-text-color: #a7fbff;
    --el-table-header-text-color: #78c9ff;
    --el-table-border-color: rgba(57, 216, 255, 0.15);
    font-size: 12px;
    cursor: pointer;
  }
}
.type-self {
  color: #00d4ff;
  font-size: 11px;
}
.type-out {
  color: #ff9f43;
  font-size: 11px;
}
.up {
  color: #2ecc71;
}
.down {
  color: #e74c3c;
}
</style>
