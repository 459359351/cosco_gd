<template>
  <div class="board-wrap">
    <dv-scroll-board :config="config" />
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { useYardStore } from "@/store/yard";

const store = useYardStore();
const config = computed(() => ({
  header: ["时间", "类型", "内容"],
  headerBGC: "rgba(40,120,220,0.55)",
  oddRowBGC: "rgba(11,38,74,0.78)",
  evenRowBGC: "rgba(8,24,52,0.78)",
  rowNum: 6,
  data: store.alerts.map((item) => [item.created_at.slice(11, 16), item.alert_type, item.message]),
}));
</script>

<style scoped>
.board-wrap {
  width: 100%;
  height: calc(100% - 36px);
  padding: 0 8px 8px;
}
</style>
