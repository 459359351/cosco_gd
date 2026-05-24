<template>
  <div class="map-wrap">
    <div ref="containerRef" class="map-core"></div>
    <canvas ref="flyCanvas" class="flyline-canvas"></canvas>
    <div class="region-switch">
      <el-segmented v-model="regionKey" :options="regionOptions" />
    </div>
    <div class="layer-switch">
      <el-segmented v-model="selection.layer" :options="layerOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ElSegmented } from "element-plus";
import { storeToRefs } from "pinia";
import { onMounted, onUnmounted, ref, watch } from "vue";

import { useAMapLoader } from "@/composables/useAMapLoader";
import { useRepairStore } from "@/store/repair";
import { useSelectionStore } from "@/store/selection";

const containerRef = ref<HTMLElement | null>(null);
const flyCanvas = ref<HTMLCanvasElement | null>(null);
const repairStore = useRepairStore();
const selection = useSelectionStore();
const { layer } = storeToRefs(selection);
const layerOptions = [
  { label: "散点", value: "point" },
  { label: "飞线", value: "flyline" },
  { label: "热力", value: "heat" },
  { label: "3D", value: "3d" },
];

const regionKey = ref<"all" | "guangdong" | "guangzhou">("all");
const regionOptions = [
  { label: "全部", value: "all" },
  { label: "广东", value: "guangdong" },
  { label: "广州", value: "guangzhou" },
];

let map: any;
let markerList: any[] = [];
let heatLayer: any = null;
let barMarkerList: any[] = [];
let flylineDots: any[] = [];
let flylineRafId: number | null = null;

interface FlylineRoute {
  start: [number, number];
  end: [number, number];
  color: string;
  coords: [number, number][];
}
let flylineRoutes: FlylineRoute[] = [];

/** 粤桂两翼默认视野 */
const MAP_DEFAULT_CENTER: [number, number] = [112.97, 23.13];
const MAP_DEFAULT_ZOOM = 6.8;

/** 所有有效坐标的网点 */
const validSites = () => (repairStore.sites || []).filter((s) => s.lng && s.lat);

/** 按地区筛选后的网点 */
const filteredSites = () => {
  const sites = validSites();
  if (regionKey.value === "guangdong") return sites.filter((s) => s.province === "广东");
  if (regionKey.value === "guangzhou") return sites.filter((s) => s.city === "广州");
  return sites;
};

const fitMapToSites = (sites: ReturnType<typeof filteredSites>) => {
  if (!map || !window.AMap) return;
  if (!sites.length) {
    map.setZoomAndCenter(MAP_DEFAULT_ZOOM, MAP_DEFAULT_CENTER, true, 500);
    return;
  }
  if (sites.length === 1) {
    map.setZoomAndCenter(9, [sites[0].lng, sites[0].lat], true, 600);
    return;
  }
  const lngs = sites.map((s) => s.lng);
  const lats = sites.map((s) => s.lat);
  const sw = new window.AMap.LngLat(Math.min(...lngs), Math.min(...lats));
  const ne = new window.AMap.LngLat(Math.max(...lngs), Math.max(...lats));
  const bounds = new window.AMap.Bounds(sw, ne);
  if (typeof map.setBounds === "function") {
    map.setBounds(bounds, true, [100, 120, 120, 120]);
  }
};

const markerColor = (type: string) =>
  type === "self" ? "#3b82f6" : "#f97316";

const redrawMarkers = () => {
  if (!map) return;
  markerList.forEach((m) => m.setMap(null));
  const sites = filteredSites();
  markerList = sites.map((site) => {
    const color = markerColor(site.company_type);
    const marker = new window.AMap.Marker({
      position: [site.lng, site.lat],
      title: site.name,
      content: `<div class="site-marker" style="--color:${color}"><span>${site.name}</span></div>`,
    });
    marker.on("mouseover", () => {
      const box = document.createElement("div");
      box.style.cssText =
        "padding:10px 14px;min-width:150px;max-width:260px;background:linear-gradient(180deg,rgba(12,40,78,0.98),rgba(4,18,40,0.98));border:1px solid rgba(80,220,255,0.55);border-radius:8px;box-shadow:0 6px 28px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.06);";
      const titleEl = document.createElement("div");
      titleEl.style.cssText = "font-weight:700;color:#8cf8ff;font-size:13px;margin-bottom:6px;";
      titleEl.textContent = site.name;
      const subEl = document.createElement("div");
      subEl.style.cssText = "font-size:12px;color:#d6eef8;line-height:1.45;";
      const typeLabel = site.company_type === "self" ? "自营" : "外包";
      subEl.textContent = site.parent_name
        ? `${typeLabel} · ${site.parent_name}`
        : typeLabel;
      box.appendChild(titleEl);
      box.appendChild(subEl);
      const tip = new window.AMap.InfoWindow({
        content: box,
        offset: new window.AMap.Pixel(0, -36),
        isCustom: true,
        closeWhenClickMap: false,
      });
      tip.open(map, marker.getPosition());
      marker.__tip = tip;
    });
    marker.on("mouseout", () => marker.__tip?.close());
    marker.setMap(map);
    return marker;
  });
  fitMapToSites(sites);
};

const clearLayers = () => {
  heatLayer?.setMap(null);
  heatLayer = null;
  barMarkerList.forEach((item) => item.setMap(null));
  barMarkerList = [];
  flylineDots.forEach((d) => d.setMap(null));
  flylineDots = [];
  flylineRoutes = [];
  if (flylineRafId !== null) {
    cancelAnimationFrame(flylineRafId);
    flylineRafId = null;
  }
  const cv = flyCanvas.value;
  if (cv) {
    const ctx = cv.getContext("2d");
    if (ctx) ctx.clearRect(0, 0, cv.width, cv.height);
  }
};

const renderHeat = () => {
  const sites = filteredSites();
  if (!sites.length) return;
  heatLayer = new window.AMap.HeatMap(map!, {
    radius: 28,
    opacity: [0.2, 0.9],
  });
  heatLayer.setDataSet({
    data: sites.map((s) => ({ lng: s.lng, lat: s.lat, count: 1 })),
    max: 1,
  });
};

const renderBar3D = () => {
  const sites = filteredSites();
  if (!sites.length) return;
  barMarkerList = sites.map((site) => {
    const color = markerColor(site.company_type);
    const barHeight = 40;
    const marker = new window.AMap.Marker({
      position: [site.lng, site.lat],
      offset: new window.AMap.Pixel(-5, -barHeight),
      content: `<div style="width:10px;height:${barHeight}px;background:linear-gradient(180deg,${color},rgba(0,0,0,0.6));box-shadow:0 0 12px ${color}88;"></div>`,
    });
    marker.setMap(map);
    return marker;
  });
};

/* ---------- 飞线：Canvas 叠加层 ---------- */

const bezierCtrl = (s: [number, number], e: [number, number]): [number, number] => {
  const dx = e[0] - s[0], dy = e[1] - s[1];
  const d = Math.sqrt(dx * dx + dy * dy);
  if (d < 1e-6) return [(s[0] + e[0]) / 2, (s[1] + e[1]) / 2];
  const off = d * 0.25;
  return [(s[0] + e[0]) / 2 + (-dy / d) * off, (s[1] + e[1]) / 2 + (dx / d) * off];
};

const bezierCoords = (s: [number, number], e: [number, number], seg = 30): [number, number][] => {
  const [cx, cy] = bezierCtrl(s, e);
  return Array.from({ length: seg + 1 }, (_, i) => {
    const t = i / seg;
    return [
      (1 - t) * (1 - t) * s[0] + 2 * (1 - t) * t * cx + t * t * e[0],
      (1 - t) * (1 - t) * s[1] + 2 * (1 - t) * t * cy + t * t * e[1],
    ] as [number, number];
  });
};

const drawFlylineCanvas = () => {
  const cv = flyCanvas.value;
  if (!cv || !map || !flylineRoutes.length) return;
  const size = map.getSize();
  const dpr = window.devicePixelRatio || 1;
  cv.width = size.width * dpr;
  cv.height = size.height * dpr;
  cv.style.width = size.width + "px";
  cv.style.height = size.height + "px";
  const ctx = cv.getContext("2d")!;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, size.width, size.height);

  for (const fl of flylineRoutes) {
    const sp = map.lngLatToContainer(new window.AMap.LngLat(fl.start[0], fl.start[1]));
    const ep = map.lngLatToContainer(new window.AMap.LngLat(fl.end[0], fl.end[1]));
    const cp = bezierCtrl(
      [sp.getX(), sp.getY()],
      [ep.getX(), ep.getY()],
    );

    ctx.beginPath();
    ctx.moveTo(sp.getX(), sp.getY());
    ctx.quadraticCurveTo(cp[0], cp[1], ep.getX(), ep.getY());
    ctx.strokeStyle = fl.color + "30";
    ctx.lineWidth = 4;
    ctx.lineCap = "round";
    ctx.stroke();

    ctx.beginPath();
    ctx.moveTo(sp.getX(), sp.getY());
    ctx.quadraticCurveTo(cp[0], cp[1], ep.getX(), ep.getY());
    ctx.strokeStyle = fl.color + "AA";
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }
};

const renderFlylines = () => {
  const sites = filteredSites();
  if (!sites.length || !map) return;

  const groups: Record<string, typeof sites> = {};
  for (const s of sites) {
    (groups[s.parent_name || "__none__"] ??= []).push(s);
  }

  flylineRoutes = [];
  for (const children of Object.values(groups)) {
    if (children.length < 2) continue;
    const cx = children.reduce((a, c) => a + c.lng, 0) / children.length;
    const cy = children.reduce((a, c) => a + c.lat, 0) / children.length;
    if (!isFinite(cx) || !isFinite(cy)) continue;
    for (const child of children) {
      if (!isFinite(child.lng) || !isFinite(child.lat)) continue;
      const color = markerColor(child.company_type);
      const coords = bezierCoords([child.lng, child.lat], [cx, cy]);
      flylineRoutes.push({ start: [child.lng, child.lat], end: [cx, cy], color, coords });
    }
  }

  drawFlylineCanvas();

  flylineDots = flylineRoutes.map((fl) => {
    const dot = new window.AMap.Marker({
      position: fl.start,
      content: `<div style="width:5px;height:5px;border-radius:50%;background:${fl.color};box-shadow:0 0 6px ${fl.color},0 0 14px ${fl.color}66;"></div>`,
      offset: new window.AMap.Pixel(-2.5, -2.5),
    });
    dot.setMap(map);
    return dot;
  });

  const anims = flylineRoutes.map((fl, i) => ({
    marker: flylineDots[i],
    coords: fl.coords,
    duration: 3000 + Math.random() * 2000,
    startTime: performance.now() + Math.random() * 3000,
  }));

  const step = (now: number) => {
    for (const a of anims) {
      const t = (((now - a.startTime) % a.duration) + a.duration) % a.duration / a.duration;
      const rawIdx = t * (a.coords.length - 1);
      const idx = Math.min(Math.floor(rawIdx), a.coords.length - 2);
      const frac = rawIdx - idx;
      const lng = a.coords[idx][0] + (a.coords[idx + 1][0] - a.coords[idx][0]) * frac;
      const lat = a.coords[idx][1] + (a.coords[idx + 1][1] - a.coords[idx][1]) * frac;
      if (isFinite(lng) && isFinite(lat)) a.marker.setPosition([lng, lat]);
    }
    flylineRafId = requestAnimationFrame(step);
  };
  flylineRafId = requestAnimationFrame(step);
};

const renderLayer = (val: string) => {
  clearLayers();
  const showMarkers = val === "point" || val === "flyline";
  markerList.forEach((m) => m.setMap(showMarkers ? map : null));
  if (val === "flyline") renderFlylines();
  if (val === "heat") renderHeat();
  if (val === "3d") renderBar3D();
};

const fullRedraw = () => {
  redrawMarkers();
  renderLayer(selection.layer);
};

onMounted(async () => {
  const AMap = await useAMapLoader();
  map = new AMap.Map(containerRef.value, {
    center: MAP_DEFAULT_CENTER,
    zoom: 7,
    viewMode: "3D",
    mapStyle: "amap://styles/darkblue",
    pitch: 40,
  });
  map.on("viewchange", () => {
    if (flylineRoutes.length) drawFlylineCanvas();
  });
  fullRedraw();
});

watch(() => repairStore.sites, fullRedraw, { deep: true });
watch(layer, (val) => renderLayer(val));
watch(regionKey, () => fullRedraw());

onUnmounted(() => {
  if (flylineRafId !== null) cancelAnimationFrame(flylineRafId);
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
.flyline-canvas {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 5;
}
.region-switch {
  position: absolute;
  right: 12px;
  top: 12px;
  z-index: 10;
}
.layer-switch {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 10;
}
</style>
