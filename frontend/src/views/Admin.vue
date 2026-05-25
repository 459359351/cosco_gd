<template>
  <div class="admin-page">
    <header class="admin-header">
      <h1>管理后台</h1>
      <el-button type="primary" link @click="router.push('/')">返回驾驶舱</el-button>
    </header>

    <el-tabs v-model="activeTab" type="border-card" class="admin-tabs">
      <el-tab-pane label="数据管理" name="data">
        <DataConsole embedded />
      </el-tab-pane>
      <el-tab-pane label="系统管理" name="system">
        <SystemAdmin embedded />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { ElButton, ElTabs, ElTabPane } from "element-plus";

import DataConsole from "@/views/DataConsole.vue";
import SystemAdmin from "@/views/SystemAdmin.vue";

const router = useRouter();
const activeTab = ref("data");
</script>

<style scoped lang="scss">
.admin-page {
  min-height: 100vh;
  padding: 20px 24px 40px;
  background: linear-gradient(180deg, #071325 0%, #0a1e38 100%);
  color: #e8f4ff;
}

.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h1 {
    margin: 0;
    font-size: 22px;
    color: #8cf0ff;
  }
}

.admin-tabs {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid rgba(80, 200, 255, 0.28);
  background: rgba(6, 22, 44, 0.35);

  :deep(.el-tabs__header) {
    margin: 0;
    background: linear-gradient(180deg, rgba(14, 52, 92, 0.98), rgba(8, 34, 62, 0.95));
    border-bottom: 1px solid rgba(80, 200, 255, 0.22);
  }

  :deep(.el-tabs__nav-wrap::after) {
    display: none;
  }

  :deep(.el-tabs__item) {
    color: #b0d4f0;
    border-color: transparent !important;
    padding: 0 18px;
    height: 42px;
    line-height: 42px;
  }

  :deep(.el-tabs__item:hover) {
    color: #e8f6ff;
  }

  :deep(.el-tabs__item.is-active) {
    color: #5cefff;
    font-weight: 600;
    background: rgba(6, 28, 55, 0.9) !important;
    border: 1px solid rgba(100, 220, 255, 0.35) !important;
    border-bottom-color: transparent !important;
    border-radius: 8px 8px 0 0;
  }

  :deep(.el-tabs--border-card) {
    background: transparent;
    border: none;
  }

  :deep(.el-tabs--border-card > .el-tabs__content) {
    padding: 0;
    background: rgba(5, 20, 42, 0.82);
  }
}
</style>
