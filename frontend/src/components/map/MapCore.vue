<template>
  <div class="map-wrap">
    <div ref="containerRef" class="map-core"></div>

    <!-- 视图模式：聚合 / 钻取 -->
    <div class="view-switch">
      <button
        v-for="opt in viewOptions"
        :key="opt.value"
        :class="{ active: repairStore.viewMode === opt.value }"
        @click="switchView(opt.value as any)"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- 公司类型过滤 -->
    <div class="company-switch">
      <button
        v-for="opt in companyOptions"
        :key="opt.value"
        :class="{ active: repairStore.companyFilter === opt.value }"
        @click="repairStore.companyFilter = opt.value as any"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- 渲染模式切换 -->
    <div class="render-switch">
      <button
        v-for="opt in renderOptions"
        :key="opt.value"
        :class="{ active: repairStore.renderMode === opt.value }"
        @click="repairStore.renderMode = opt.value as any"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- 区域切换 -->
    <div class="region-switch">
      <button
        v-for="opt in regionOptions"
        :key="opt.value"
        :class="{ active: repairStore.regionFilter === opt.value }"
        @click="repairStore.regionFilter = opt.value as any"
      >
        {{ opt.label }}
      </button>
    </div>

    <!-- 钻取返回 -->
    <div v-if="repairStore.viewMode === 'drilldown'" class="back-btn">
      <button @click="backToAggregate">← 返回聚合</button>
    </div>

    <!-- 当前选中信息 -->
    <div v-if="repairStore.selectedParent" class="drilldown-info">
      {{ repairStore.selectedParent }} — {{ drilldownSites.length }} 个网点
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";

import { useAMapLoader } from "@/composables/useAMapLoader";
import { useRepairStore } from "@/store/repair";

const containerRef = ref<HTMLElement | null>(null);
const repairStore = useRepairStore();

/* ---------- 状态从 Store 读取 ---------- */
const viewOptions = [
  { label: "聚合", value: "aggregate" },
  { label: "网点", value: "drilldown" },
];

const companyOptions = [
  { label: "全部", value: "all" },
  { label: "自营", value: "self" },
  { label: "外包", value: "outsourced" },
];

const renderOptions = [
  { label: "点位", value: "point" },
  { label: "热力", value: "heat" },
  { label: "3D", value: "3d" },
];

const regionOptions = [
  { label: "全部", value: "all" },
  { label: "广东", value: "guangdong" },
  { label: "广西", value: "guangxi" },
];

/* ---------- 高德地图实例 ---------- */
let map: any;
let markerList: any[] = [];
let aggregateMarkerList: any[] = [];
let heatLayer: any = null;
let barMarkerList: any[] = [];
let infoWindow: any = null;

const MAP_DEFAULT_CENTER: [number, number] = [112.97, 23.13];
const MAP_DEFAULT_ZOOM = 6.8;

/* ---------- 渲染状态管理 ---------- */
let renderGeneration = 0;
let recomputeLabels: (() => void) | null = null;
let mapDebounceTimer: ReturnType<typeof setTimeout> | null = null;

const wait = (ms: number) => new Promise<void>((r) => setTimeout(r, ms));

/* ---------- 数据过滤 ---------- */
const validSites = () => (repairStore.sites || []).filter((s) => s.lng && s.lat);

const filteredSites = () => {
  const sites = validSites();
  if (repairStore.regionFilter === "guangdong") return sites.filter((s) => s.province === "广东");
  if (repairStore.regionFilter === "guangxi") return sites.filter((s) => s.province === "广西");
  return sites;
};

/* ---------- 标签力导向防重叠 ---------- */
const LABEL_W = 100;
const LABEL_H = 40;
const PAD = 6;
const MIN_LEN = 30;
const MAX_LEN = 120;
const MAX_ITER = 80;

const computeNoOverlapOffsets = (items: { key: string; lng: number; lat: number }[]) => {
  const offsets = new Map<string, { dx: number; dy: number }>();
  if (!map || items.length === 0) return offsets;

  /* 单项：直接返回默认偏移，无需碰撞计算 */
  if (items.length === 1) {
    offsets.set(items[0].key, { dx: 0, dy: -40 });
    return offsets;
  }

  // 转为屏幕坐标 + 记住原点
  const labels = items.map((d) => {
    const px = map.lngLatToContainer(new window.AMap.LngLat(d.lng, d.lat));
    return {
      key: d.key,
      ox: px.x,       // 圆点屏幕坐标
      oy: px.y,
      x: px.x,        // 标签当前屏幕坐标（底部中心）
      y: px.y - 40,   // 初始：圆点正上方 40px
    };
  });

  const hw = LABEL_W / 2 + PAD;
  const hh = LABEL_H + PAD;

  for (let iter = 0; iter < MAX_ITER; iter++) {
    let hasOverlap = false;
    const forces = labels.map(() => ({ fx: 0, fy: 0 }));

    for (let i = 0; i < labels.length; i++) {
      for (let j = i + 1; j < labels.length; j++) {
        const a = labels[i], b = labels[j];
        // 标签边界框
        const ax1 = a.x - hw, ay1 = a.y - hh, ax2 = a.x + hw, ay2 = a.y;
        const bx1 = b.x - hw, by1 = b.y - hh, bx2 = b.x + hw, by2 = b.y;
        const ox = Math.min(ax2, bx2) - Math.max(ax1, bx1);
        const oy = Math.min(ay2, by2) - Math.max(ay1, by1);

        if (ox > 0 && oy > 0) {
          hasOverlap = true;
          const area = ox * oy;
          // 沿两者中心连线方向推开
          let dx = a.x - b.x;
          let dy = a.y - b.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          dx /= dist;
          dy /= dist;
          const force = 5 + area * 0.03;
          forces[i].fx += dx * force;
          forces[i].fy += dy * force;
          forces[j].fx -= dx * force;
          forces[j].fy -= dy * force;
        }
      }
    }

    if (!hasOverlap) break;

    // 应用力 + 限制距离
    for (let i = 0; i < labels.length; i++) {
      labels[i].x += forces[i].fx;
      labels[i].y += forces[i].fy;
      // 限制标签离圆点的最大距离
      const rdx = labels[i].x - labels[i].ox;
      const rdy = labels[i].y - labels[i].oy;
      const dist = Math.sqrt(rdx * rdx + rdy * rdy);
      if (dist > MAX_LEN) {
        const scale = MAX_LEN / dist;
        labels[i].x = labels[i].ox + rdx * scale;
        labels[i].y = labels[i].oy + rdy * scale;
      }
      // 保证最小距离（不贴到圆点上）
      if (dist > 0 && dist < MIN_LEN) {
        const scale = MIN_LEN / dist;
        labels[i].x = labels[i].ox + rdx * scale;
        labels[i].y = labels[i].oy + rdy * scale;
      }
    }
  }

  for (const lab of labels) {
    offsets.set(lab.key, { dx: Math.round(lab.x - lab.ox), dy: Math.round(lab.y - lab.oy) });
  }
  return offsets;
};

/* ---------- 聚合数据计算 ---------- */
interface AggregateItem {
  parentName: string;
  lat: number;
  lng: number;
  qty: number;
  revenue: number;
  companyType: string;
  qtyWow: number;
  siteCount: number;
}

const aggregateData = computed((): AggregateItem[] => {
  const sites = filteredSites();
  const selfOrgs = repairStore.selfOrgs || [];
  const outOrgs = repairStore.outsourcedOrgs || [];

  // 按 parent_name 分组
  const groups: Record<string, typeof sites> = {};
  sites.forEach((s) => {
    const key = s.parent_name || s.name;
    if (!groups[key]) groups[key] = [];
    groups[key].push(s);
  });

  return Object.entries(groups).map(([parentName, groupSites]) => {
    const lat = groupSites.reduce((sum, s) => sum + s.lat, 0) / groupSites.length;
    const lng = groupSites.reduce((sum, s) => sum + s.lng, 0) / groupSites.length;
    const companyType = groupSites[0]?.company_type || "self";

    // 匹配 org 数据
    const org = [...selfOrgs, ...outOrgs].find((o) => o.org_name === parentName);
    const qty = org?.container_qty || groupSites.length * 50;
    const revenue = org?.revenue || 0;
    const qtyWow = org?.qty_wow || 0;

    return { parentName, lat, lng, qty, revenue, companyType, qtyWow, siteCount: groupSites.length };
  });
});

const filteredAggregate = computed(() => {
  let data = aggregateData.value;
  const f = repairStore.companyFilter;
  if (f === "self") {
    data = data.filter((d) => d.companyType === "self");
  } else if (f === "outsourced") {
    data = data.filter((d) => d.companyType === "outsourced");
  }
  return data;
});

/* ---------- 钻取网点 ---------- */
const drilldownSites = computed(() => {
  if (!repairStore.selectedParent) return [];
  return filteredSites().filter((s) => s.parent_name === repairStore.selectedParent);
});

/* ---------- 颜色 ---------- */
const markerColor = (type: string) => (type === "self" ? "#3b82f6" : "#f97316");
const alertColor = "#ff4757";
const thirdColor = "#2ecc71";

/* ---------- HTML 生成辅助 ---------- */
function aggregateBubbleHtml(item: AggregateItem, dx: number, dy: number) {
  const isAlert = item.qtyWow < 0;
  const color = isAlert ? alertColor : markerColor(item.companyType);
  const lineLen = Math.sqrt(dx * dx + dy * dy).toFixed(1);
  const lineAngle = (Math.atan2(dy, dx) * 180 / Math.PI - 90).toFixed(1);
  return `
    <div class="aggregate-bubble" style="--color:${color};--dx:${dx}px;--dy:${dy}px;--line-len:${lineLen}px;--line-angle:${lineAngle}deg;"
         data-alert="${isAlert ? '1' : '0'}">
      <div class="bubble-pin"></div>
      <div class="bubble-callout"></div>
      <div class="bubble-body">
        <div class="bubble-name">${item.parentName}</div>
        <div class="bubble-qty">${item.qty.toLocaleString()}<span class="bubble-unit">箱</span></div>
      </div>
    </div>`;
}

function aggregateDotHtml(item: AggregateItem) {
  const isAlert = item.qtyWow < 0;
  const color = isAlert ? alertColor : markerColor(item.companyType);
  return `
    <div class="aggregate-bubble" style="--color:${color};" data-alert="${isAlert ? '1' : '0'}">
      <div class="bubble-pin"></div>
    </div>`;
}

function siteLabelHtml(name: string, color: string, dx: number, dy: number) {
  const lineLen = Math.sqrt(dx * dx + dy * dy).toFixed(1);
  const lineAngle = (Math.atan2(dy, dx) * 180 / Math.PI - 90).toFixed(1);
  return `
    <div class="site-marker" style="--color:${color};--dx:${dx}px;--dy:${dy}px;--line-len:${lineLen}px;--line-angle:${lineAngle}deg;">
      <div class="site-callout"></div>
      <span class="site-label">${name}</span>
      <div class="site-dot"></div>
    </div>`;
}

function siteDotHtml(color: string) {
  return `<div class="site-marker" style="--color:${color};"><div class="site-dot"></div></div>`;
}

/* ---------- 地图操作 ---------- */
const fitToSites = (sites: { lng: number; lat: number }[]) => {
  if (!map || !window.AMap || !sites.length) return;
  if (sites.length === 1) {
    map.setZoomAndCenter(12, [sites[0].lng, sites[0].lat], true, 600);
    return;
  }
  const lngs = sites.map((s) => s.lng);
  const lats = sites.map((s) => s.lat);
  const sw = new window.AMap.LngLat(Math.min(...lngs), Math.min(...lats));
  const ne = new window.AMap.LngLat(Math.max(...lngs), Math.max(...lats));
  const bounds = new window.AMap.Bounds(sw, ne);
  map.setBounds(bounds, true, [80, 80, 80, 80]);
};

/* ---------- 清除所有图层 ---------- */
const clearLayers = () => {
  markerList.forEach((m) => m.setMap(null));
  markerList = [];
  aggregateMarkerList.forEach((m) => m.setMap(null));
  aggregateMarkerList = [];
  barMarkerList.forEach((m) => m.setMap(null));
  barMarkerList = [];
  heatLayer?.setMap(null);
  heatLayer = null;
  if (infoWindow) {
    infoWindow.close();
    infoWindow = null;
  }
};

/* ---------- 创建信息框 ---------- */
const showInfo = (position: [number, number], html: string) => {
  if (!map) return;
  if (infoWindow) infoWindow.close();
  infoWindow = new window.AMap.InfoWindow({
    content: html,
    offset: new window.AMap.Pixel(0, -20),
    isCustom: true,
    closeWhenClickMap: true,
  });
  infoWindow.open(map, position);
};

/* ---------- 聚合气泡渲染（两阶段异步） ---------- */
const renderAggregate = async () => {
  if (!map) return;
  const gen = ++renderGeneration;
  clearLayers();
  recomputeLabels = null;

  const data = filteredAggregate.value;
  if (!data.length) return;

  /* 阶段一：只渲染定位点 + 动画地图 */
  aggregateMarkerList = data.map((item) => {
    const marker = new window.AMap.Marker({
      position: [item.lng, item.lat],
      content: aggregateDotHtml(item),
      offset: new window.AMap.Pixel(0, 0),
    });

    marker.on("click", () => {
      repairStore.drilldown(item.parentName);
    });

    marker.on("mouseover", () => {
      const isAlert = item.qtyWow < 0;
      const color = isAlert ? alertColor : markerColor(item.companyType);
      const html = `
        <div style="padding:10px 14px;background:linear-gradient(180deg,rgba(12,40,78,0.98),rgba(4,18,40,0.98));
          border:1px solid ${color};border-radius:8px;min-width:160px;">
          <div style="font-weight:700;color:${color};font-size:13px;margin-bottom:6px;">${item.parentName}</div>
          <div style="font-size:12px;color:#d6eef8;line-height:1.6;">
            <div>箱量: ${item.qty.toLocaleString()} 个</div>
            <div>收入: ${(item.revenue / 10000).toFixed(2)} 万元</div>
            <div>网点: ${item.siteCount} 个</div>
            <div style="color:${item.qtyWow >= 0 ? '#2ecc71' : '#ff4757'}">环比: ${item.qtyWow >= 0 ? '+' : ''}${item.qtyWow}</div>
          </div>
        </div>
      `;
      showInfo([item.lng, item.lat], html);
    });

    marker.setMap(map);
    return marker;
  });

  fitToSites(data);

  /* 阶段二：等待动画完成后计算偏移 + 渲染引线标签 */
  await wait(700);
  if (gen !== renderGeneration) return; // 已被新渲染取消

  const labelItems = data.map((d) => ({ key: d.parentName, lng: d.lng, lat: d.lat }));

  const applyAggregateLabels = () => {
    if (!map) return;
    const offsets = computeNoOverlapOffsets(labelItems);
    data.forEach((item, i) => {
      const marker = aggregateMarkerList[i];
      if (!marker) return;
      const off = offsets.get(item.parentName);
      const dx = off?.dx ?? 0;
      const dy = off?.dy ?? -40;
      marker.setContent(aggregateBubbleHtml(item, dx, dy));
    });
  };

  recomputeLabels = applyAggregateLabels;
  applyAggregateLabels();
};

/* ---------- 渲染所有网点（两阶段异步） ---------- */
const renderAllSites = async () => {
  if (!map) return;
  const gen = ++renderGeneration;
  clearLayers();
  recomputeLabels = null;

  let sites = filteredSites();

  // 按公司类型过滤
  const cf = repairStore.companyFilter;
  if (cf === "self") {
    sites = sites.filter((s) => s.company_type === "self");
  } else if (cf === "outsourced") {
    sites = sites.filter((s) => s.company_type === "outsourced");
  }

  if (!sites.length) return;

  // 按 parent 分组，每组只显示 1 个标签（去重）
  const parentGroups: Record<string, typeof sites> = {};
  sites.forEach((s) => {
    const p = s.parent_name || s.name;
    if (!parentGroups[p]) parentGroups[p] = [];
    parentGroups[p].push(s);
  });
  const topSites = new Set<string>();
  Object.values(parentGroups).forEach((group) => {
    const sorted = [...group].sort((a, b) => a.name.length - b.name.length);
    if (sorted[0]) topSites.add(sorted[0].name);
  });

  /* 阶段一：渲染点 + 动画 */
  markerList = sites.map((site) => {
    const color = markerColor(site.company_type);
    const marker = new window.AMap.Marker({
      position: [site.lng, site.lat],
      content: siteDotHtml(color),
    });

    marker.on("click", () => {
      repairStore.drilldown(site.parent_name || site.name);
    });

    marker.on("mouseover", () => {
      const html = `
        <div style="padding:10px 14px;background:linear-gradient(180deg,rgba(12,40,78,0.98),rgba(4,18,40,0.98));
          border:1px solid ${color};border-radius:8px;min-width:150px;">
          <div style="font-weight:700;color:#8cf8ff;font-size:13px;margin-bottom:6px;">${site.name}</div>
          <div style="font-size:12px;color:#d6eef8;line-height:1.45;">
            ${site.company_type === "self" ? "自营" : "外包"} · ${site.parent_name || ""}
          </div>
        </div>
      `;
      showInfo([site.lng, site.lat], html);
    });

    marker.setMap(map);
    return marker;
  });

  fitToSites(sites);

  /* 阶段二：等待动画完成后计算偏移 + 渲染引线标签 */
  await wait(700);
  if (gen !== renderGeneration) return;

  const labeledSites = sites.filter((s) => topSites.has(s.name));
  const labelItems = labeledSites.map((s) => ({ key: s.name, lng: s.lng, lat: s.lat }));

  const applySiteLabels = () => {
    if (!map) return;
    const offsets = computeNoOverlapOffsets(labelItems);
    sites.forEach((site, i) => {
      const marker = markerList[i];
      if (!marker) return;
      const color = markerColor(site.company_type);
      if (!topSites.has(site.name)) return; // 无标签的网点保持只有点
      const off = offsets.get(site.name);
      const dx = off?.dx ?? 0;
      const dy = off?.dy ?? -40;
      marker.setContent(siteLabelHtml(site.name, color, dx, dy));
    });
  };

  recomputeLabels = applySiteLabels;
  applySiteLabels();
};

/* ---------- 钻取网点渲染（两阶段异步，所有网点都有引线+标签） ---------- */
const renderDrilldown = async () => {
  if (!map) return;
  const gen = ++renderGeneration;
  clearLayers();
  recomputeLabels = null;

  const sites = drilldownSites.value;
  if (!sites.length) return;

  // 按公司类型过滤
  let displaySites = sites;
  const cf = repairStore.companyFilter;
  if (cf === "self") {
    displaySites = sites.filter((s) => s.company_type === "self");
  } else if (cf === "outsourced") {
    displaySites = sites.filter((s) => s.company_type === "outsourced");
  }

  if (!displaySites.length) return;

  /* 阶段一：渲染点 + 动画 */
  markerList = displaySites.map((site) => {
    const color = markerColor(site.company_type);
    const marker = new window.AMap.Marker({
      position: [site.lng, site.lat],
      content: siteDotHtml(color),
    });

    marker.on("mouseover", () => {
      const html = `
        <div style="padding:10px 14px;background:linear-gradient(180deg,rgba(12,40,78,0.98),rgba(4,18,40,0.98));
          border:1px solid ${color};border-radius:8px;min-width:150px;">
          <div style="font-weight:700;color:#8cf8ff;font-size:13px;margin-bottom:6px;">${site.name}</div>
          <div style="font-size:12px;color:#d6eef8;line-height:1.45;">
            ${site.company_type === "self" ? "自营" : "外包"} · ${site.parent_name || ""}
          </div>
        </div>
      `;
      showInfo([site.lng, site.lat], html);
    });

    marker.setMap(map);
    return marker;
  });

  fitToSites(displaySites);

  /* 阶段二：等待动画完成后计算偏移 + 所有网点渲染引线标签 */
  await wait(700);
  if (gen !== renderGeneration) return;

  const labelItems = displaySites.map((s) => ({ key: s.name, lng: s.lng, lat: s.lat }));

  const applyDrilldownLabels = () => {
    if (!map) return;
    const offsets = computeNoOverlapOffsets(labelItems);
    displaySites.forEach((site, i) => {
      const marker = markerList[i];
      if (!marker) return;
      const color = markerColor(site.company_type);
      const off = offsets.get(site.name);
      const dx = off?.dx ?? 0;
      const dy = off?.dy ?? -40;
      marker.setContent(siteLabelHtml(site.name, color, dx, dy));
    });
  };

  recomputeLabels = applyDrilldownLabels;
  applyDrilldownLabels();
};

/* ---------- 热力图渲染 ---------- */
const renderHeat = () => {
  if (!map) return;
  clearLayers();
  recomputeLabels = null;

  /* 轮播/钻取时只显示当前机构的网点 */
  const sp = repairStore.selectedParent;
  let sites = sp ? drilldownSites.value : filteredSites();
  const cf = repairStore.companyFilter;
  if (cf === "self") sites = sites.filter((s) => s.company_type === "self");
  else if (cf === "outsourced") sites = sites.filter((s) => s.company_type === "outsourced");
  if (!sites.length) return;

  heatLayer = new window.AMap.HeatMap(map, {
    radius: 28,
    opacity: [0.2, 0.9],
  });
  heatLayer.setDataSet({
    data: sites.map((s) => ({ lng: s.lng, lat: s.lat, count: 1 })),
    max: 1,
  });

  if (sp) fitToSites(sites);
};

/* ---------- 3D 柱状图渲染 ---------- */
const renderBar3D = () => {
  if (!map) return;
  clearLayers();
  recomputeLabels = null;

  /* 轮播/钻取时只显示当前机构的网点 */
  const sp = repairStore.selectedParent;
  let sites = sp ? drilldownSites.value : filteredSites();
  const cf = repairStore.companyFilter;
  if (cf === "self") sites = sites.filter((s) => s.company_type === "self");
  else if (cf === "outsourced") sites = sites.filter((s) => s.company_type === "outsourced");
  if (!sites.length) return;

  barMarkerList = sites.map((site) => {
    const color = markerColor(site.company_type);
    const barHeight = 40;
    const marker = new window.AMap.Marker({
      position: [site.lng, site.lat],
      offset: new window.AMap.Pixel(-5, -barHeight),
      content: `<div style="width:10px;height:${barHeight}px;
          background:linear-gradient(180deg,${color},rgba(0,0,0,0.6));
          box-shadow:0 0 12px ${color}88;"></div>`,
    });
    marker.setMap(map);
    return marker;
  });

  if (sp) fitToSites(sites);
};

/* ---------- 视图切换（委托给 Store） ---------- */
const switchView = (mode: "aggregate" | "drilldown") => {
  repairStore.switchView(mode);
  if (mode === "aggregate") {
    map?.setZoomAndCenter(MAP_DEFAULT_ZOOM, MAP_DEFAULT_CENTER, true, 500);
  }
};

const backToAggregate = () => {
  repairStore.clearDrilldown();
  map?.setZoomAndCenter(MAP_DEFAULT_ZOOM, MAP_DEFAULT_CENTER, true, 500);
};

/* ---------- 地图缩放/拖拽后重算引线 ---------- */
const onMapViewportChange = () => {
  if (mapDebounceTimer) clearTimeout(mapDebounceTimer);
  mapDebounceTimer = setTimeout(() => {
    if (recomputeLabels) recomputeLabels();
  }, 300);
};

/* ---------- 全量重绘 ---------- */
const fullRedraw = async () => {
  const rm = repairStore.renderMode;
  const vm = repairStore.viewMode;
  const sp = repairStore.selectedParent;

  if (rm === "heat") {
    renderHeat();
    return;
  }
  if (rm === "3d") {
    renderBar3D();
    return;
  }

  if (vm === "drilldown") {
    if (sp) {
      await renderDrilldown();
    } else {
      await renderAllSites();
    }
  } else {
    await renderAggregate();
  }
};

/* ---------- 生命周期 ---------- */
onMounted(async () => {
  const AMap = await useAMapLoader();
  map = new AMap.Map(containerRef.value, {
    center: MAP_DEFAULT_CENTER,
    zoom: MAP_DEFAULT_ZOOM,
    viewMode: "3D",
    mapStyle: "amap://styles/darkblue",
    pitch: 40,
  });

  /* 监听地图缩放/拖拽，重算引线 */
  map.on("zoomend", onMapViewportChange);
  map.on("moveend", onMapViewportChange);

  fullRedraw();
});

/* ---------- 监听（合并为单一数组 watch，避免同一 tick 多次触发） ---------- */
watch(
  [
    () => repairStore.sites,
    () => repairStore.selfOrgs,
    () => repairStore.outsourcedOrgs,
    () => repairStore.viewMode,
    () => repairStore.companyFilter,
    () => repairStore.renderMode,
    () => repairStore.regionFilter,
    () => repairStore.selectedParent,
  ],
  fullRedraw,
  { deep: true, flush: "post" },
);

onUnmounted(() => {
  if (mapDebounceTimer) clearTimeout(mapDebounceTimer);
  map?.off("zoomend", onMapViewportChange);
  map?.off("moveend", onMapViewportChange);
  map?.destroy();
});
</script>

<style scoped lang="scss">
.map-wrap {
  position: relative;
  width: 100%;
  height: 100%;
}
.map-core {
  width: 100%;
  height: 100%;
}

/* 聚合气泡样式 — 胶囊形 */
:global(.aggregate-bubble) {
  position: relative;
  width: 0;
  height: 0;
  cursor: pointer;
  transition: transform 0.25s ease;
}
:global(.aggregate-bubble:hover) {
  z-index: 100;
}
/* 底部定位点（始终在原点） */
:global(.aggregate-bubble .bubble-pin) {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color);
  box-shadow: 0 0 10px var(--color), 0 0 20px var(--color)44;
  border: 2px solid rgba(255, 255, 255, 0.4);
  transform: translate(-50%, -50%);
  transition: all 0.25s ease;
}
:global(.aggregate-bubble:hover .bubble-pin) {
  box-shadow: 0 0 16px var(--color), 0 0 30px var(--color)66;
  transform: translate(-50%, -50%) scale(1.3);
}
:global(.aggregate-bubble[data-alert="1"] .bubble-pin) {
  animation: pin-pulse 1.6s ease-in-out infinite;
}
@keyframes pin-pulse {
  0%, 100% { box-shadow: 0 0 10px #ff4757, 0 0 20px #ff475744; }
  50% { box-shadow: 0 0 18px #ff4757, 0 0 36px #ff475766; }
}
/* 引线 */
:global(.aggregate-bubble .bubble-callout) {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 1.5px;
  height: var(--line-len, 40px);
  background: var(--color);
  opacity: 0;
  transform-origin: top center;
  transform: translateX(-50%) rotate(var(--line-angle, 0deg));
  pointer-events: none;
  box-shadow: 0 0 4px var(--color);
  animation: callout-fadein 0.35s ease forwards;
}
/* 胶囊标签（通过 CSS 变量定位） */
:global(.aggregate-bubble .bubble-body) {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(calc(-50% + var(--dx, 0px)), calc(-100% + var(--dy, -40px)));
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-width: 72px;
  max-width: 150px;
  padding: 5px 14px;
  background: rgba(4, 14, 28, 0.92);
  border: 1px solid var(--color);
  border-radius: 999px;
  color: #e0f0ff;
  backdrop-filter: blur(6px);
  pointer-events: none;
  white-space: nowrap;
  transition: transform 0.25s ease;
  animation: callout-fadein 0.35s ease forwards;
}
:global(.aggregate-bubble:hover .bubble-body) {
  transform: translate(calc(-50% + var(--dx, 0px)), calc(-100% + var(--dy, -40px))) scale(1.08);
}
:global(.bubble-name) {
  font-size: 11px;
  font-weight: 600;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.9);
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}
:global(.bubble-qty) {
  font-size: 13px;
  font-weight: 700;
  text-shadow: 0 0 4px rgba(0, 0, 0, 0.9);
  line-height: 1.2;
  margin-top: 1px;
}
:global(.bubble-unit) {
  font-size: 10px;
  font-weight: 400;
  opacity: 0.75;
  margin-left: 2px;
}

/* 引线 & 标签淡入动画 */
@keyframes callout-fadein {
  from { opacity: 0; }
  to { opacity: 1; }
}

/* 网点标记样式 */
:global(.site-marker) {
  position: relative;
  width: 0;
  height: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
}
:global(.site-marker .site-dot) {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color);
  box-shadow: 0 0 10px var(--color);
  border: 2px solid rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: all 0.2s ease;
}
:global(.site-marker:hover .site-dot) {
  transform: translate(-50%, -50%) scale(1.3);
  box-shadow: 0 0 16px var(--color);
}
/* 引线 */
:global(.site-marker .site-callout) {
  position: absolute;
  left: 50%;
  top: 50%;
  width: 1.5px;
  height: var(--line-len, 28px);
  background: var(--color);
  opacity: 0;
  transform-origin: top center;
  transform: translateX(-50%) rotate(var(--line-angle, 0deg));
  pointer-events: none;
  box-shadow: 0 0 4px var(--color);
  animation: callout-fadein 0.35s ease forwards;
}
:global(.site-marker .site-label) {
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(calc(-50% + var(--dx, 0px)), calc(-100% + var(--dy, -40px)));
  white-space: nowrap;
  font-size: 11px;
  color: #e0f0ff;
  background: rgba(6, 14, 31, 0.75);
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid rgba(57, 216, 255, 0.2);
  pointer-events: none;
  transition: transform 0.2s ease;
  animation: callout-fadein 0.35s ease forwards;
}
:global(.site-marker:hover .site-label) {
  transform: translate(calc(-50% + var(--dx, 0px)), calc(-100% + var(--dy, -40px))) scale(1.08);
  z-index: 100;
}

/* 控制按钮 */
.view-switch,
.company-switch,
.render-switch,
.region-switch {
  position: absolute;
  z-index: 10;
  display: flex;
  gap: 4px;
  border-radius: 8px;
  padding: 5px;
}
/* 一级控件：视图切换 — 更高不透明度 + 填充式 active */
.view-switch {
  left: 12px;
  top: 12px;
  background: rgba(4, 14, 28, 0.92);
  border: 1px solid rgba(57, 216, 255, 0.35);
  backdrop-filter: blur(8px);
  button {
    padding: 6px 18px;
    font-size: 13px;
    font-weight: 600;
    border-radius: 6px;
    background: transparent;
    color: rgba(168, 201, 255, 0.6);
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    &:hover {
      color: rgba(168, 201, 255, 0.95);
      background: rgba(0, 212, 255, 0.08);
    }
    &.active {
      background: rgba(0, 212, 255, 0.2);
      color: #00d4ff;
      border-color: rgba(0, 212, 255, 0.55);
      box-shadow: 0 0 12px rgba(0, 212, 255, 0.15);
    }
  }
}
/* 返回按钮 — 紧跟视图切换下方 */
.back-btn {
  position: absolute;
  left: 12px;
  top: 56px;
  z-index: 10;
  background: rgba(4, 14, 28, 0.92);
  border: 1px solid rgba(57, 216, 255, 0.35);
  border-radius: 8px;
  padding: 5px;
  backdrop-filter: blur(8px);
  button {
    padding: 5px 14px;
    font-size: 12px;
    border-radius: 6px;
    background: transparent;
    color: rgba(168, 201, 255, 0.7);
    border: 1px solid transparent;
    cursor: pointer;
    transition: all 0.2s ease;
    &:hover {
      color: #ff6b6b;
      background: rgba(255, 107, 107, 0.08);
    }
  }
}
/* 二级控件：区域切换 */
.region-switch {
  right: 12px;
  top: 12px;
  background: rgba(4, 14, 28, 0.88);
  border: 1px solid rgba(57, 216, 255, 0.25);
  backdrop-filter: blur(6px);
}
/* 三级控件：过滤 + 渲染 */
.company-switch,
.render-switch {
  right: 12px;
  background: rgba(4, 14, 28, 0.88);
  border: 1px solid rgba(57, 216, 255, 0.25);
  backdrop-filter: blur(6px);
}
.company-switch {
  bottom: 50px;
}
.render-switch {
  bottom: 12px;
}

.drilldown-info {
  position: absolute;
  left: 50%;
  bottom: 12px;
  transform: translateX(-50%);
  z-index: 10;
  background: rgba(4, 14, 28, 0.92);
  border: 1px solid rgba(57, 216, 255, 0.35);
  border-radius: 8px;
  padding: 8px 20px;
  font-size: 15px;
  font-weight: 600;
  color: #00d4ff;
  pointer-events: none;
  backdrop-filter: blur(6px);
}

/* 通用二级按钮 */
.company-switch button,
.render-switch button,
.region-switch button {
  padding: 5px 14px;
  font-size: 12px;
  border: 1px solid transparent;
  background: transparent;
  color: rgba(168, 201, 255, 0.65);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.25s ease;
  min-width: 48px;
  &:hover {
    color: rgba(168, 201, 255, 0.9);
    background: rgba(0, 212, 255, 0.06);
  }
  &.active {
    background: rgba(0, 212, 255, 0.15);
    border-color: rgba(0, 212, 255, 0.45);
    color: #00d4ff;
  }
}
</style>
