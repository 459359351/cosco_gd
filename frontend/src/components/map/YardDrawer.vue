<template>
  <el-drawer
    v-model="visible"
    title="堆场详情"
    direction="rtl"
    size="360px"
    :with-header="true"
    :before-close="onClose"
  >
    <div v-if="detail" class="content">
      <div class="item"><span>名称</span><strong>{{ detail.yard.name }}</strong></div>
      <div class="item"><span>编码</span><strong>{{ detail.yard.code }}</strong></div>
      <div class="item"><span>地区</span><strong>{{ detail.yard.province }}-{{ detail.yard.city }}</strong></div>
      <div class="item"><span>今日进场</span><strong>{{ detail.today_in_teu }}</strong></div>
      <div class="item"><span>今日出场</span><strong>{{ detail.today_out_teu }}</strong></div>
      <div class="item"><span>当前库存</span><strong>{{ detail.stock_teu }}</strong></div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ElDrawer } from "element-plus";
import { computed, ref, watch } from "vue";

import { getYardDetail } from "@/api/dashboard";
import { useSelectionStore } from "@/store/selection";

const selection = useSelectionStore();
const visible = computed({
  get: () => selection.drawerYardId !== null,
  set: (val) => {
    if (!val) selection.closeYardDetailDrawer();
  },
});
const detail = ref<any>(null);

watch(
  () => selection.drawerYardId,
  async (id) => {
    if (!id) {
      detail.value = null;
      return;
    }
    detail.value = await getYardDetail(id);
  },
  { immediate: true },
);

const onClose = (done: () => void) => {
  selection.closeYardDetailDrawer();
  done();
};
</script>

<style scoped lang="scss">
.content {
  display: grid;
  gap: 12px;
}
.item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  border-radius: 6px;
  background: rgba(9, 38, 69, 0.72);
}
.item span {
  color: #85c9f5;
}
.item strong {
  color: #cbf7ff;
}
</style>
