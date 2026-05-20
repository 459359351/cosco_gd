<template>
  <div class="panel-title">
    <span>{{ title }}</span>
    <div class="line"></div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string }>();
</script>

<style scoped lang="scss">
.panel-title {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px 6px;
  color: #9be7ff;
  font-weight: 600;
}
.line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, #3be0ff, transparent);
}
</style>
