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
import { useRealtimeStore } from "@/store/realtime";
import { useSelectionStore } from "@/store/selection";
import { useYardStore } from "@/store/yard";

const containerRef = ref<HTMLElement | null>(null);
const yardStore = useYardStore();
const selection = useSelectionStore();
const realtime = useRealtimeStore();
const { yardId, layer } = storeToRefs(selection);
const { alertPulseYardId } = storeToRefs(realtime);
const layerOptions = [
  { label: "散点", value: "point" },
  { label: "热力", value: "heat" },
  { label: "飞线", value: "flow" },
  { label: "3D", value: "3d" },
];

let map: any;
let markerList: any[] = [];
let heatLayer: any = null;
let barMarkerList: any[] = [];
/** 飞线：原生 Polyline + CircleMarker，避免 Loca 与地图 WebGL 状态冲突 */
let flowPolylineList: any[] = [];
let flowHeadMarkers: any[] = [];
let flowTracks: Array<{
  track: [number, number][];
  weight: number;
  speed: number;
  progress: number;
  phase: number;
}> = [];
let flowAnimTimer: number | null = null;

const disposeFlowGraphics = () => {
  if (flowAnimTimer) {
    window.clearInterval(flowAnimTimer);
    flowAnimTimer = null;
  }
  flowTracks = [];
  flowPolylineList.forEach((p) => {
    try {
      p.setMap(null);
    } catch {
      /* ignore */
    }
  });
  flowPolylineList = [];
  flowHeadMarkers.forEach((m) => {
    try {
      m.setMap(null);
    } catch {
      /* ignore */
    }
  });
  flowHeadMarkers = [];
};

/** 粤桂两翼默认视野；无点位时回退 */
const MAP_DEFAULT_CENTER: [number, number] = [112.97, 23.13];
const MAP_DEFAULT_ZOOM = 6.8;

/** 按当前堆场列表调整视野（省份筛选、首屏加载时调用） */
const fitMapToYards = () => {
  if (!map || !window.AMap) return;
  const yards = yardStore.yards;
  if (!yards.length) {
    map.setZoomAndCenter(MAP_DEFAULT_ZOOM, MAP_DEFAULT_CENTER, true, 500);
    return;
  }
  if (yards.length === 1) {
    const y = yards[0];
    map.setZoomAndCenter(9, [y.lng, y.lat], true, 600);
    return;
  }
  const lngs = yards.map((y) => y.lng);
  const lats = yards.map((y) => y.lat);
  const sw = new window.AMap.LngLat(Math.min(...lngs), Math.min(...lats));
  const ne = new window.AMap.LngLat(Math.max(...lngs), Math.max(...lats));
  const bounds = new window.AMap.Bounds(sw, ne);
  const padding = [100, 120, 120, 120];
  if (typeof map.setBounds === "function") {
    map.setBounds(bounds, true, padding);
    return;
  }
  if (typeof map.setFitView === "function") {
    map.setFitView(markerList.filter(Boolean), false, padding, 14);
  }
};

const redrawMarkers = async () => {
  if (!map) return;
  markerList.forEach((m) => m.setMap(null));
  markerList = yardStore.yards.map((yard) => {
    const marker = new window.AMap.Marker({
      position: [yard.lng, yard.lat],
      title: yard.name,
      content: `<div class="yard-marker ${yard.status}">${yard.name}</div>`,
    });
    marker.on("click", () => selection.focusYard(yard.id, { openDrawer: true }));
    marker.on("mouseover", () => {
      const box = document.createElement("div");
      box.style.cssText =
        "padding:10px 14px;min-width:150px;max-width:260px;background:linear-gradient(180deg,rgba(12,40,78,0.98),rgba(4,18,40,0.98));border:1px solid rgba(80,220,255,0.55);border-radius:8px;box-shadow:0 6px 28px rgba(0,0,0,0.5),inset 0 1px 0 rgba(255,255,255,0.06);";
      const titleEl = document.createElement("div");
      titleEl.style.cssText = "font-weight:700;color:#8cf8ff;font-size:13px;margin-bottom:6px;letter-spacing:0.3px;";
      titleEl.textContent = yard.name;
      const subEl = document.createElement("div");
      subEl.style.cssText = "font-size:12px;color:#d6eef8;line-height:1.45;";
      subEl.textContent = `容量 ${yard.capacity}`;
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
  fitMapToYards();
};

const locateYard = (id: number | null) => {
  if (!id || !map) return;
  const yard =
    yardStore.yards.find((item) => item.id === id) ||
    yardStore.rankingItems.find((item: { id: number }) => item.id === id);
  if (yard && typeof yard.lng === "number" && typeof yard.lat === "number") {
    map.setZoomAndCenter(9, [yard.lng, yard.lat], true, 800);
  }
};

const pulseAlert = (id: number | null) => {
  if (!id) return;
  const marker = markerList[yardStore.yards.findIndex((y) => y.id === id)];
  if (marker) {
    marker.setAnimation("AMAP_ANIMATION_BOUNCE");
    setTimeout(() => marker.setAnimation(null), 1800);
  }
};

const clearLayers = () => {
  heatLayer?.setMap(null);
  heatLayer = null;
  disposeFlowGraphics();

  barMarkerList.forEach((item) => item.setMap(null));
  barMarkerList = [];
};

const renderHeat = () => {
  heatLayer = new window.AMap.HeatMap(map, {
    radius: 28,
    opacity: [0.2, 0.9],
  });
  heatLayer.setDataSet({
    data: yardStore.yards.map((y) => ({ lng: y.lng, lat: y.lat, count: y.capacity })),
    max: Math.max(...yardStore.yards.map((x) => x.capacity), 100),
  });
};

const renderFlow = () => {
  disposeFlowGraphics();

  if (!map) return;

  const yardByCode = new Map(yardStore.yards.map((item) => [item.code, item]));
  const validFlows = yardStore.odFlow
    .map((flow) => {
      const from = yardByCode.get(flow.from_code);
      const to = yardByCode.get(flow.to_code);
      if (!from || !to) return null;
      return { from, to, value: flow.value };
    })
    .filter(Boolean);

  if (!validFlows.length) return;

  const minValue = Math.min(...validFlows.map((item: any) => item.value));
  const maxValue = Math.max(...validFlows.map((item: any) => item.value));
  const valueSpan = Math.max(1, maxValue - minValue);
  const normalize = (value: number) => (value - minValue) / valueSpan;

  const makeTrack = (from: any, to: any) => {
    const midLng = (from.lng + to.lng) / 2;
    const midLat = (from.lat + to.lat) / 2 + 0.35;
    const points: [number, number][] = [];
    for (let i = 0; i <= 80; i++) {
      const t = i / 80;
      const lng = (1 - t) * (1 - t) * from.lng + 2 * (1 - t) * t * midLng + t * t * to.lng;
      const lat = (1 - t) * (1 - t) * from.lat + 2 * (1 - t) * t * midLat + t * t * to.lat;
      points.push([lng, lat]);
    }
    return points;
  };

  validFlows.forEach((item: any) => {
    const track = makeTrack(item.from, item.to);
    const normalized = normalize(item.value);
    const w = 1.8 + normalized * 3.8;
    const speed = 0.85 + normalized * 2.2;
    flowTracks.push({
      track,
      weight: w,
      speed,
      progress: Math.random() * track.length,
      phase: Math.random() * Math.PI * 2,
    });

    const poly = new window.AMap.Polyline({
      path: track,
      strokeColor: `rgba(61,210,255,${0.45 + normalized * 0.35})`,
      strokeWeight: Math.max(2, 2 + normalized * 5),
      strokeOpacity: 0.92,
      lineJoin: "round",
      lineCap: "round",
      zIndex: 52,
    });
    poly.setMap(map);
    flowPolylineList.push(poly);
  });

  flowTracks.forEach((flow) => {
    const idx = Math.floor(flow.progress) % flow.track.length;
    const head = new window.AMap.CircleMarker({
      center: flow.track[idx],
      radius: Math.min(8, Math.max(3, flow.weight)),
      strokeColor: "rgba(200,248,255,0.95)",
      strokeWeight: 1,
      fillColor: "#f0fdff",
      fillOpacity: 0.95,
      zIndex: 60,
    });
    head.setMap(map);
    flowHeadMarkers.push(head);
  });

  flowAnimTimer = window.setInterval(() => {
    flowTracks.forEach((flow, i) => {
      flow.progress = (flow.progress + flow.speed) % flow.track.length;
      const idx = Math.floor(flow.progress);
      const pt = flow.track[idx];
      const hm = flowHeadMarkers[i];
      if (hm && typeof hm.setCenter === "function") {
        hm.setCenter(pt);
      }
    });
  }, 90);
};

const renderBar3D = () => {
  barMarkerList = yardStore.yards.map((yard) => {
    const barHeight = Math.max(20, Math.floor(yard.capacity / 180));
    const marker = new window.AMap.Marker({
      position: [yard.lng, yard.lat],
      offset: new window.AMap.Pixel(-5, -barHeight),
      content: `<div style="width:10px;height:${barHeight}px;background:linear-gradient(180deg,#6cf7ff,#1654ff);box-shadow:0 0 12px rgba(83,215,255,0.8);"></div>`,
    });
    marker.setMap(map);
    return marker;
  });
};

const renderLayer = (val: string) => {
  clearLayers();
  markerList.forEach((m) => m.setMap(val === "point" ? map : null));
  if (val === "heat") renderHeat();
  if (val === "flow") renderFlow();
  if (val === "3d") renderBar3D();
};

onMounted(async () => {
  const AMap = await useAMapLoader();
  map = new AMap.Map(containerRef.value, {
    center: [112.97, 23.13],
    zoom: 7,
    viewMode: "3D",
    mapStyle: "amap://styles/darkblue",
    pitch: 40,
  });
  await redrawMarkers();
  renderLayer(selection.layer);
});

watch(() => yardStore.yards, redrawMarkers, { deep: true });
watch(yardId, locateYard);
watch(alertPulseYardId, pulseAlert);
watch(layer, (val) => renderLayer(val));
watch(() => yardStore.odFlow, () => {
  if (selection.layer === "flow") renderFlow();
}, { deep: true });

onUnmounted(() => {
  disposeFlowGraphics();
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
