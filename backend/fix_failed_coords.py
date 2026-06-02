import asyncio
import asyncpg
import aiohttp
import json

DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"
AMAP_KEY = "26d9ac20e8f589851bbd5b17c3d4cff4"

# 上次失败的网点，换不同的搜索关键词
SITES_TO_FIX = [
    ("深圳运营中心_汕头堆场", "汕头市濠江区广澳街道", "广东", "汕头"),
    ("深圳运营中心_汕头广澳", "汕头市濠江区广澳港区", "广东", "汕头"),
    ("南宁亿邦_广西梧州赤水港", "梧州市长洲区赤水村", "广西", "梧州"),
    ("广州运营中心_惠州龙溪", "惠州市博罗县龙溪街道", "广东", "惠州"),
    ("广州弘运_江门天马港", "江门市新会区天马村", "广东", "江门"),
    ("广州弘运_新会亚太", "江门市新会区双水镇", "广东", "江门"),
    ("广州弘运_新会新港", "江门市新会区会城街道", "广东", "江门"),
    ("深圳运营中心_深圳大铲湾", "深圳市宝安区大铲湾", "广东", "深圳"),
    ("广州运营中心_淡水河码头", "广州市增城区新塘镇", "广东", "广州"),
    ("广州运营中心_新沙港", "广州港新沙港区", "广东", "东莞"),
]


async def geocode_amap(session, address, city_hint):
    url = "https://restapi.amap.com/v3/geocode/geo"
    params = {
        "key": AMAP_KEY,
        "address": address,
        "city": city_hint,
        "output": "JSON",
    }
    try:
        async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get("status") == "1" and data.get("geocodes"):
                    loc = data["geocodes"][0]["location"]
                    lng, lat = map(float, loc.split(","))
                    province = data["geocodes"][0].get("province", "")
                    city = data["geocodes"][0].get("city", "")
                    return {"lng": lng, "lat": lat, "province": province, "city": city, "formatted": data["geocodes"][0].get("formatted_address", "")}
    except Exception as e:
        print(f"  API error: {e}")
    return None


async def main():
    conn = await asyncpg.connect(DB_URL)
    try:
        results = []
        async with aiohttp.ClientSession() as session:
            for code, address, expect_prov, expect_city in SITES_TO_FIX:
                print(f"[{code}] {address}")
                result = await geocode_amap(session, address, expect_city)
                await asyncio.sleep(0.1)

                if result:
                    lng, lat = result["lng"], result["lat"]
                    actual_prov = result["province"]
                    actual_city = result["city"]
                    prov_ok = expect_prov in actual_prov or actual_prov in expect_prov
                    city_ok = expect_city in actual_city or actual_city in expect_city

                    print(f"  -> {lng:.6f}, {lat:.6f} | {actual_prov} {actual_city} | {result['formatted']}")

                    if not prov_ok:
                        print(f"  [WARN] 省份不匹配: 期望 {expect_prov}, 实际 {actual_prov}")
                    if not city_ok:
                        print(f"  [WARN] 城市不匹配: 期望 {expect_city}, 实际 {actual_city}")

                    results.append({
                        "code": code,
                        "address": address,
                        "lng": lng,
                        "lat": lat,
                        "province": expect_prov,
                        "city": expect_city,
                        "actual_province": actual_prov,
                        "actual_city": actual_city,
                        "formatted": result["formatted"],
                        "prov_ok": prov_ok,
                        "city_ok": city_ok,
                    })
                else:
                    print(f"  -> [FAILED]")
                    results.append({
                        "code": code,
                        "address": address,
                        "failed": True,
                    })

        with open("geocode_results2.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        fixed = 0
        for r in results:
            if not r.get("failed"):
                await conn.execute(
                    "UPDATE repair_network_sites SET lng=$1, lat=$2, province=$3, city=$4 WHERE code=$5",
                    round(r["lng"], 6), round(r["lat"], 6), r["province"], r["city"], r["code"]
                )
                fixed += 1

        print(f"\n完成: {fixed}/{len(SITES_TO_FIX)} 个网点已更新")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
