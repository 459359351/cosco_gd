<template>
  <div class="screen-wrapper">
    <header class="header panel">
      <div class="header-left">
        <WeekSelector />
      </div>
      <div class="title">
        集装箱修理业务驾驶舱
      </div>
      <div class="meta">
        <span>{{ now }}</span>
      </div>
    </header>

    <aside class="left-top panel">
      <slot name="left-top" />
    </aside>
    <aside class="left-mid panel">
      <slot name="left-mid" />
    </aside>
    <aside class="left-bottom panel">
      <slot name="left-bottom" />
    </aside>

    <main class="center panel">
      <slot name="center" />
    </main>

    <aside class="right-top panel">
      <slot name="right-top" />
    </aside>
    <aside class="right-bottom panel">
      <slot name="right-bottom" />
    </aside>

    <footer class="footer panel">
      <slot name="footer" />
    </footer>
  </div>
</template>

<script setup lang="ts">
import { useNow } from "@vueuse/core";
import { computed } from "vue";

import WeekSelector from "@/components/header/WeekSelector.vue";

const nowRef = useNow({ interval: 1000 });
const now = computed(() => nowRef.value.toLocaleString("zh-CN"));
</script>

<style scoped lang="scss">
/* 基于 vw/vh 的弹性布局，适配 1080p ~ 2K+ 任意分辨率 */
.screen-wrapper {
  position: relative;
  display: grid;
  grid-template-columns: clamp(320px, 21.875vw, 500px) 1fr clamp(320px, 21.875vw, 500px);
  grid-template-rows: clamp(50px, 6.5vh, 72px) 1fr 1fr clamp(280px, 30vh, 420px);
  gap: max(5px, 0.93vh) max(5px, 0.52vw);
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  &::after {
    content: "";
    pointer-events: none;
    position: absolute;
    inset: 0;
    background-image: linear-gradient(
      rgba(59, 207, 255, 0.02) 50%,
      rgba(8, 24, 48, 0.02) 50%
    );
    background-size: 100% calc(100vh / 270);
    mix-blend-mode: screen;
    opacity: 0.45;
    z-index: 1000;
  }
}
.panel {
  border: 1px solid rgba(57, 216, 255, 0.35);
  background: linear-gradient(180deg, rgba(8, 28, 56, 0.88), rgba(4, 14, 28, 0.88));
  box-shadow: inset 0 0 30px rgba(26, 174, 255, 0.16);
  border-radius: max(4px, 0.42vw);
  overflow: hidden;
  min-height: 0;
}
.header {
  grid-column: 1 / 4;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 clamp(10px, 1.04vw, 24px);
  position: relative;
  overflow: visible;
  z-index: 10;
}
.header-left {
  position: absolute;
  left: clamp(10px, 1.04vw, 24px);
  z-index: 5001;
}
.title {
  font-size: clamp(20px, 2.8vw, 36px);
  letter-spacing: 1px;
  color: #7ee7ff;
  text-shadow: 0 0 12px rgba(84, 229, 255, 0.65);
}
.meta {
  position: absolute;
  right: clamp(10px, 1.04vw, 24px);
  display: flex;
  gap: max(8px, 0.73vw);
  align-items: center;
  font-size: clamp(11px, 0.83vw, 16px);
  color: rgba(168, 201, 255, 0.7);
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
  display: none;
}
.center {
  grid-column: 2;
  grid-row: 2 / 4;
  position: relative;
  z-index: 2;
  overflow: hidden;
}
.right-top {
  grid-column: 3;
  grid-row: 2;
}
.right-bottom {
  grid-column: 3;
  grid-row: 3;
}
.footer {
  grid-column: 1 / 4;
  grid-row: 4;
  min-height: 0;
  display: flex;
  flex-direction: row;
  gap: max(5px, 0.52vw);
}
</style>
