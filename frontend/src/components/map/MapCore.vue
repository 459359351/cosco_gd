<template>
  <div class="map-wrap">
    <div ref="containerRef" class="map-core"></div>
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
const repairStore = useRepairStore();
const selection = useSelectionStore();
const { layer } = storeToRefs(selection);
const layerOptions = [
  { label: "散点", value: "point" },
  { label: "热力", value: "heat" },
  { label: "3D", value: "3d" },
];

let map: any;
let markerList: any[] = [];
let heatLayer: any = null;
let barMarkerList: any[] = [];

/** 粤桂两翼默认视野 */
const MAP_DEFAULT_CENTER: [number, number] = [112.97, 23.13];
const MAP_DEFAULT_ZOOM = 6.8;

/** 只有有效坐标的网点 */
const validSites = () => (repairStore.sites || []).filter((s) => s.lng && s.lat);

const fitMapToSites = () => {
  if (!map || !window.AMap) return;
  const sites = validSites();
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
  const padding = [100, 120, 120, 120];
  if (typeof map.setBounds === "function") {
    map.setBounds(bounds, true, padding);
  }
};

const markerColor = (type: string) =>
  type === "self" ? "#3b82f6" : "#f97316";

const redrawMarkers = () => {
  if (!map) return;
  markerList.forEach((m) => m.setMap(null));
  markerList = validSites().map((site) => {
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
  fitMapToSites();
};

const clearLayers = () => {
  heatLayer?.setMap(null);
  heatLayer = null;
  barMarkerList.forEach((item) => item.setMap(null));
  barMarkerList = [];
};

const renderHeat = () => {
  const sites = validSites();
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
  const sites = validSites();
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

const renderLayer = (val: string) => {
  clearLayers();
  markerList.forEach((m) => m.setMap(val === "point" ? map : null));
  if (val === "heat") renderHeat();
  if (val === "3d") renderBar3D();
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
  redrawMarkers();
  renderLayer(selection.layer);
});

watch(() => repairStore.sites, redrawMarkers, { deep: true });
watch(layer, (val) => renderLayer(val));

onUnmounted(() => {
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
.layer-switch {
  position: absolute;
  right: 12px;
  bottom: 12px;
  z-index: 10;
}
</style>
