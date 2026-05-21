import { useAMapLoader } from "@/composables/useAMapLoader";

export type GeocodeResult = {
  province: string;
  city: string;
  lng: number;
  lat: number;
  formattedAddress?: string;
};

function stripSuffix(name: string): string {
  return name.replace(/(省|市|自治区|壮族自治区|回族自治区|维吾尔自治区|特别行政区)$/u, "").trim();
}

function normalizeProvince(raw: string): string {
  const s = stripSuffix(raw);
  if (s.includes("广东")) return "广东";
  if (s.includes("广西")) return "广西";
  return s || raw;
}

function normalizeCity(raw: string): string {
  return stripSuffix(raw) || raw;
}

export async function geocodeAddress(
  address: string,
  hintCity?: string,
): Promise<GeocodeResult | null> {
  const text = address.trim();
  if (!text) return null;

  const AMap = await useAMapLoader();
  const geocoder = new AMap.Geocoder({ city: hintCity || "全国" });

  return new Promise((resolve, reject) => {
    geocoder.getLocation(text, (status: string, result: any) => {
      if (status !== "complete" || result?.info !== "OK") {
        reject(new Error(result?.info || "地址解析失败"));
        return;
      }
      const geo = result.geocodes?.[0];
      if (!geo?.location) {
        reject(new Error("未找到匹配坐标"));
        return;
      }
      const comp = geo.addressComponent || {};
      const province = normalizeProvince(comp.province || "");
      const city = normalizeCity(comp.city || comp.district || "");
      resolve({
        province,
        city,
        lng: Number(geo.location.lng),
        lat: Number(geo.location.lat),
        formattedAddress: geo.formattedAddress,
      });
    });
  });
}
