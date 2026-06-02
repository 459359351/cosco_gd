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
  gap: max(6px, 0.52vw);
  padding: max(5px, 0.93vh) max(8px, 0.62vw) max(3px, 0.56vh);
  color: #9be7ff;
  font-weight: 600;
  font-size: clamp(12px, 0.83vw, 16px);
  flex-shrink: 0;
}
.line {
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, #3be0ff, transparent);
}
</style>
