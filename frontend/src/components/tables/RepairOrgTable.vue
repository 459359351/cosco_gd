<template>
  <div class="org-table-wrap">
    <div class="org-table-scroll" ref="scrollRef">
      <table class="org-table">
        <thead>
          <tr>
            <th class="col-name">名称</th>
            <th class="col-type">类型</th>
            <th class="col-qty">箱量</th>
            <th class="col-rev">收入(万)</th>
            <th class="col-wow">环比</th>
          </tr>
        </thead>
      </table>
      <div class="org-table-body">
        <table class="org-table">
          <!-- 列表重复两遍实现无缝循环 -->
          <tbody v-for="round in copies" :key="round">
            <tr v-for="row in allOrgs" :key="round + '-' + row.org_code" @click="onRowClick(row)">
              <td class="col-name"><span class="name-text">{{ row.org_name }}</span></td>
              <td class="col-type">
                <span :class="row.company_type === 'self' ? 'type-self' : 'type-out'">
                  {{ row.company_type === "self" ? "自营" : "外包" }}
                </span>
              </td>
              <td class="col-qty">{{ row.container_qty?.toLocaleString() }}</td>
              <td class="col-rev">{{ (row.revenue / 10000).toFixed(1) }}</td>
              <td class="col-wow">
                <span :class="row.qty_wow > 0 ? 'up' : row.qty_wow < 0 ? 'down' : ''">
                  {{ row.qty_wow > 0 ? "+" : "" }}{{ row.qty_wow }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";

import { useRepairStore } from "@/store/repair";

const store = useRepairStore();
const scrollRef = ref<HTMLElement | null>(null);
const copies = ref(1);
let scrollRaf: number | null = null;

const allOrgs = computed(() => {
  return [...store.selfOrgs, ...store.outsourcedOrgs].sort((a, b) => b.revenue - a.revenue);
});

function onRowClick(row: any) {
  store.drilldown(row.org_name);
}

function startAutoScroll() {
  stopAutoScroll();
  const body = scrollRef.value?.querySelector(".org-table-body") as HTMLElement | null;
  if (!body) return;
  body.scrollTop = 0;
  const firstTbody = body.querySelector("table tbody") as HTMLElement | null;
  if (!firstTbody) return;
  /* 一份数据能放下就不重复、不滚动 */
  if (firstTbody.offsetHeight <= body.clientHeight) {
    copies.value = 1;
    return;
  }
  copies.value = 2;
  const singleH = firstTbody.offsetHeight;
  const speed = 0.25;
  let acc = 0;

  const step = () => {
    if (!body) return;
    acc += speed;
    if (acc >= 1) {
      acc -= 1;
      body.scrollTop += 1;
      if (body.scrollTop >= singleH) {
        body.scrollTop = 0;
      }
    }
    scrollRaf = requestAnimationFrame(step);
  };
  scrollRaf = requestAnimationFrame(step);
}

function stopAutoScroll() {
  if (scrollRaf !== null) {
    cancelAnimationFrame(scrollRaf);
    scrollRaf = null;
  }
}

watch(allOrgs, async () => {
  stopAutoScroll();
  await nextTick();
  startAutoScroll();
});

onMounted(() => {
  startAutoScroll();
});

onBeforeUnmount(() => {
  stopAutoScroll();
});
</script>

<style scoped lang="scss">
.org-table-wrap {
  height: 100%;
  overflow: hidden;
}
.org-table-scroll {
  height: 100%;
  display: flex;
  flex-direction: column;
}
.org-table-body {
  flex: 1;
  overflow: auto;
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
.org-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  color: #a7fbff;
  th {
    position: sticky;
    top: 0;
    background: rgba(13, 43, 79, 0.8);
    color: #78c9ff;
    text-align: left;
    padding: 4px 8px;
    font-weight: 600;
    border-bottom: 1px solid rgba(57, 216, 255, 0.15);
  }
  td {
    padding: 3px 8px;
    border-bottom: 1px solid rgba(57, 216, 255, 0.08);
  }
  tbody tr {
    cursor: pointer;
    transition: background 0.2s;
    &:hover {
      background: rgba(0, 212, 255, 0.08);
    }
  }
}
.col-name {
  min-width: 120px;
}
.name-text {
  display: inline-block;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.col-type {
  width: 50px;
}
.col-qty {
  width: 70px;
  text-align: right;
}
.col-rev {
  width: 70px;
  text-align: right;
}
.col-wow {
  width: 60px;
  text-align: right;
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
