import AMapLoader from "@amap/amap-jsapi-loader";

let loadedPromise: Promise<any> | null = null;

export async function useAMapLoader() {
  if (!loadedPromise) {
    loadedPromise = AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY || "",
      version: "2.0",
      plugins: ["AMap.Scale", "AMap.ToolBar", "AMap.ControlBar", "AMap.HeatMap"],
    });
  }
  return loadedPromise;
}
