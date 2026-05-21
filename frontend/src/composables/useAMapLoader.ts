import AMapLoader from "@amap/amap-jsapi-loader";

const security = import.meta.env.VITE_AMAP_SECURITY as string | undefined;
if (security && typeof window !== "undefined") {
  (window as unknown as { _AMapSecurityConfig?: { securityJsCode: string } })._AMapSecurityConfig = {
    securityJsCode: security,
  };
}

let loadedPromise: Promise<any> | null = null;

export async function useAMapLoader() {
  if (!loadedPromise) {
    loadedPromise = AMapLoader.load({
      key: import.meta.env.VITE_AMAP_KEY || "",
      version: "2.0",
      plugins: ["AMap.Scale", "AMap.ToolBar", "AMap.ControlBar", "AMap.HeatMap", "AMap.Geocoder"],
    });
  }
  return loadedPromise;
}
