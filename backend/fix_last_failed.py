import asyncio
import asyncpg
import aiohttp
import json

DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"
AMAP_KEY = "26d9ac20e8f589851bbd5b17c3d4cff4"

SITES_TO_FIX = [
    ("广州运营中心_惠州龙溪", "博罗县龙溪街道", "广东", "惠州"),
    ("深圳运营中心_深圳大铲湾", "深圳港大铲湾港区", "广东", "深圳"),
    ("广州运营中心_淡水河码头", "广州市增城区新塘镇港口大道", "广东", "广州"),
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
                    print(f"  -> {lng:.6f}, {lat:.6f} | {result['province']} {result['city']} | {result['formatted']}")
                    results.append({
                        "code": code,
                        "address": address,
                        "lng": lng,
                        "lat": lat,
                        "province": expect_prov,
                        "city": expect_city,
                        "formatted": result["formatted"],
                    })
                else:
                    print(f"  -> [FAILED]")
                    results.append({"code": code, "address": address, "failed": True})

        fixed = 0
        for r in results:
            if not r.get("failed"):
                await conn.execute(
                    "UPDATE repair_network_sites SET lng=$1, lat=$2, province=$3, city=$4 WHERE code=$5",
                    round(r["lng"], 6), round(r["lat"], 6), r["province"], r["city"], r["code"]
                )
                fixed += 1

        print(f"\n完成: {fixed}/{len(SITES_TO_FIX)}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
