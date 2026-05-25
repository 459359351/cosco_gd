<template>
  <div class="screen-wrapper">
    <header class="header panel">
      <div class="title">集装箱修理业务驾驶舱</div>
      <div class="meta">
        <span>{{ now }}</span>
      </div>
    </header>

    <aside class="left-top panel"><slot name="left-top" /></aside>
    <aside class="left-mid panel"><slot name="left-mid" /></aside>
    <aside class="left-bottom panel"><slot name="left-bottom" /></aside>

    <main class="center panel"><slot name="center" /></main>

    <aside class="right-top panel"><slot name="right-top" /></aside>
    <aside class="right-bottom panel"><slot name="right-bottom" /></aside>

    <footer class="footer panel"><slot name="footer" /></footer>
  </div>
</template>

<script setup lang="ts">
import { useNow } from "@vueuse/core";
import { computed } from "vue";

const nowRef = useNow({ interval: 1000 });
const now = computed(() => nowRef.value.toLocaleString("zh-CN"));
</script>

<style scoped lang="scss">
.screen-wrapper {
  position: relative;
  display: grid;
  grid-template-columns: 420px 1fr 420px;
  grid-template-rows: 88px 260px 210px 1fr 125px;
  gap: 10px;
  width: 1920px;
  height: 1080px;
  &::after {
    content: "";
    pointer-events: none;
    position: absolute;
    inset: 0;
    background-image: linear-gradient(
      rgba(59, 207, 255, 0.02) 50%,
      rgba(8, 24, 48, 0.02) 50%
    );
    background-size: 100% 4px;
    mix-blend-mode: screen;
    opacity: 0.45;
  }
}
.panel {
  border: 1px solid rgba(57, 216, 255, 0.35);
  background: linear-gradient(180deg, rgba(8, 28, 56, 0.88), rgba(4, 14, 28, 0.88));
  box-shadow: inset 0 0 30px rgba(26, 174, 255, 0.16);
  border-radius: 8px;
  overflow: hidden;
}
.header {
  grid-column: 1 / 4;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.title {
  font-size: 30px;
  letter-spacing: 1px;
  color: #7ee7ff;
  text-shadow: 0 0 12px rgba(84, 229, 255, 0.65);
}
.meta {
  display: flex;
  gap: 14px;
  align-items: center;
}
.left-top {
  grid-column: 1;
  grid-row: 2;
}
.left-mid {
  grid-column: 1;
  grid-row: 3;
}
.left-bottom {
  grid-column: 1;
  grid-row: 4;
}
.center {
  grid-column: 2;
  grid-row: 2 / 5;
  position: relative;
  z-index: 2;
}
.right-top {
  grid-column: 3;
  grid-row: 2 / 4;
}
.right-bottom {
  grid-column: 3;
  grid-row: 4;
}
.footer {
  grid-column: 1 / 4;
  grid-row: 5;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
</style>
