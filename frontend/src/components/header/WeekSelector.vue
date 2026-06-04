<template>
  <div
    ref="selectorRef"
    class="week-selector"
  >
    <!-- 触发按钮 -->
    <div
      class="week-trigger"
      @click="toggleDropdown"
    >
      <span class="week-trigger-label">{{ weekStore.selectedLabel }}</span>
      <span
        v-if="weekStore.selectedDateRange"
        class="week-trigger-range"
      >
        {{ weekStore.selectedDateRange }}
      </span>
      <span
        class="week-trigger-arrow"
        :class="{ open: isOpen }"
      >▾</span>
    </div>

    <!-- 下拉列表 + 预览弹窗 -->
    <Transition name="dropdown">
      <div
        v-if="isOpen"
        class="week-dropdown"
      >
        <!-- 周列表 -->
        <div
          ref="listRef"
          class="week-list"
        >
          <div
            v-for="w in weekStore.weeks"
            :key="`${w.year}-${w.week}`"
            :ref="(el) => setItemRef(w, el)"
            class="week-item"
            :class="{
              active: isSelected(w),
            }"
            @mouseenter="onWeekHover(w)"
            @mouseleave="onWeekLeave"
            @click="onWeekClick(w)"
          >
            <!-- 时间轴圆点 -->
            <div
              class="week-timeline-dot"
              :class="{ active: isSelected(w) }"
            />
            <div class="week-item-info">
              <span class="week-item-label">{{ w.week_label }}</span>
              <span class="week-item-range">{{ w.date_range }}</span>
            </div>
          </div>
        </div>

        <!-- Hover 预览弹窗 -->
        <Transition name="preview">
          <WeekPreviewPopup
            v-if="weekStore.previewData && weekStore.hoveredWeek"
            :data="weekStore.previewData"
            :week="weekStore.hoveredWeek"
            :top="popupTop"
          />
        </Transition>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { type ComponentPublicInstance, onBeforeUnmount, onMounted, ref } from "vue";

import type { AvailableWeekItem } from "@/api/repairDashboard";
import WeekPreviewPopup from "@/components/header/WeekPreviewPopup.vue";
import { useWeekStore } from "@/store/week";

const weekStore = useWeekStore();

const isOpen = ref(false);
const selectorRef = ref<HTMLElement | null>(null);
const listRef = ref<HTMLElement | null>(null);
const popupTop = ref(0);

/** 存储每个 week-item 的 DOM 引用，用于计算弹窗位置 */
const itemRefs = ref<Map<string, HTMLElement>>(new Map());

function setItemRef(w: AvailableWeekItem, el: Element | ComponentPublicInstance | null) {
  if (el) {
    const htmlEl = el instanceof HTMLElement ? el : (el as ComponentPublicInstance).$el;
    itemRefs.value.set(`${w.year}-${w.week}`, htmlEl as HTMLElement);
  }
}

function isSelected(w: AvailableWeekItem) {
  return w.year === weekStore.selectedYear && w.week === weekStore.selectedWeek;
}

function toggleDropdown() {
  isOpen.value = !isOpen.value;
  if (!isOpen.value) {
    weekStore.clearHover();
  }
}

/* ---------- Hover 交互（带防抖） ---------- */
let hoverTimer: ReturnType<typeof setTimeout> | null = null;

function onWeekHover(w: AvailableWeekItem) {
  // 清除之前的定时器
  if (hoverTimer) clearTimeout(hoverTimer);

  weekStore.hoveredWeek = w;

  // 计算弹窗垂直位置（相对于下拉列表顶部）
  const key = `${w.year}-${w.week}`;
  const el = itemRefs.value.get(key);
  if (el && listRef.value) {
    const listRect = listRef.value.getBoundingClientRect();
    const itemRect = el.getBoundingClientRect();
    popupTop.value = itemRect.top - listRect.top;
  }

  // 200ms 防抖后获取预览数据
  hoverTimer = setTimeout(() => {
    weekStore.fetchPreview(w.year, w.week);
  }, 200);
}

function onWeekLeave() {
  if (hoverTimer) {
    clearTimeout(hoverTimer);
    hoverTimer = null;
  }
  weekStore.clearHover();
}

/* ---------- 点击选中 ---------- */
function onWeekClick(w: AvailableWeekItem) {
  weekStore.selectWeek(w.year, w.week);
  isOpen.value = false;
  weekStore.clearHover();
}

/* ---------- 点击外部关闭 ---------- */
function onClickOutside(e: MouseEvent) {
  if (selectorRef.value && !selectorRef.value.contains(e.target as Node)) {
    isOpen.value = false;
    weekStore.clearHover();
  }
}

onMounted(() => {
  document.addEventListener("click", onClickOutside);
});

onBeforeUnmount(() => {
  document.removeEventListener("click", onClickOutside);
  if (hoverTimer) clearTimeout(hoverTimer);
});
</script>

<style scoped lang="scss">
.week-selector {
  position: relative;
  z-index: 5000;
  user-select: none;
}

/* --- 触发按钮 --- */
.week-trigger {
  display: flex;
  align-items: center;
  gap: max(4px, 0.3vw);
  padding: max(4px, 0.4vh) max(8px, 0.5vw);
  border: 1px solid rgba(57, 216, 255, 0.35);
  border-radius: max(4px, 0.25vw);
  background: linear-gradient(180deg, rgba(8, 28, 56, 0.9), rgba(4, 14, 28, 0.9));
  cursor: pointer;
  transition: all 0.25s ease;

  &:hover {
    border-color: rgba(57, 216, 255, 0.6);
    box-shadow: 0 0 10px rgba(0, 212, 255, 0.15);
  }
}

.week-trigger-label {
  font-size: clamp(11px, 0.75vw, 14px);
  font-weight: 600;
  color: #7ee7ff;
  white-space: nowrap;
}

.week-trigger-range {
  font-size: clamp(9px, 0.6vw, 12px);
  color: rgba(168, 201, 255, 0.6);
}

.week-trigger-arrow {
  font-size: clamp(10px, 0.6vw, 12px);
  color: rgba(168, 201, 255, 0.5);
  transition: transform 0.25s ease;

  &.open {
    transform: rotate(180deg);
  }
}

/* --- 下拉面板 --- */
.week-dropdown {
  position: absolute;
  top: calc(100% + max(4px, 0.4vh));
  left: 0;
  display: flex;
  min-width: max(180px, 12vw);
}

.week-list {
  width: 100%;
  max-height: 40vh;
  overflow-y: auto;
  background: rgba(4, 14, 28, 0.96);
  border: 1px solid rgba(57, 216, 255, 0.35);
  border-radius: max(6px, 0.35vw);
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5), 0 0 15px rgba(0, 212, 255, 0.1);
  padding: max(4px, 0.3vh) 0;

  /* 自定义滚动条 */
  &::-webkit-scrollbar {
    width: 4px;
  }

  &::-webkit-scrollbar-track {
    background: transparent;
  }

  &::-webkit-scrollbar-thumb {
    background: rgba(57, 216, 255, 0.3);
    border-radius: 2px;
  }
}

/* --- 周条目 --- */
.week-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: max(6px, 0.4vw);
  padding: max(6px, 0.5vh) max(10px, 0.6vw) max(6px, 0.5vh) max(14px, 0.8vw);
  cursor: pointer;
  transition: all 0.2s ease;
  border-left: 3px solid transparent;

  /* 时间轴竖线（::before） */
  &::before {
    content: "";
    position: absolute;
    left: max(6px, 0.45vw);
    top: 0;
    bottom: 0;
    width: 1px;
    background: rgba(57, 216, 255, 0.15);
  }

  &:first-child::before {
    top: 50%;
  }

  &:last-child::before {
    bottom: 50%;
  }

  &:hover {
    background: rgba(0, 212, 255, 0.08);
    border-left-color: rgba(126, 231, 255, 0.5);
  }

  &.active {
    background: rgba(0, 212, 255, 0.12);
    border-left-color: #00d4ff;

    .week-item-label {
      color: #7ee7ff;
    }
  }
}

/* 时间轴圆点 */
.week-timeline-dot {
  position: relative;
  z-index: 1;
  width: max(6px, 0.4vw);
  height: max(6px, 0.4vw);
  border-radius: 50%;
  background: rgba(57, 216, 255, 0.4);
  border: 1px solid rgba(57, 216, 255, 0.6);
  flex-shrink: 0;
  transition: all 0.2s ease;

  &.active {
    background: #00d4ff;
    box-shadow: 0 0 6px rgba(0, 212, 255, 0.5);
  }

  .week-item:hover & {
    background: rgba(126, 231, 255, 0.7);
    box-shadow: 0 0 8px rgba(84, 229, 255, 0.4);
  }
}

.week-item-info {
  display: flex;
  flex-direction: column;
  gap: 1px;
}

.week-item-label {
  font-size: clamp(10px, 0.7vw, 13px);
  font-weight: 600;
  color: #c0deff;
  white-space: nowrap;
}

.week-item-range {
  font-size: clamp(8px, 0.55vw, 11px);
  color: rgba(168, 201, 255, 0.5);
}

/* --- 下拉动画 --- */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* --- 预览弹窗动画 --- */
.preview-enter-active,
.preview-leave-active {
  transition: opacity 0.15s ease;
}

.preview-enter-from,
.preview-leave-to {
  opacity: 0;
}
</style>
