import asyncio
import asyncpg
import aiohttp

DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"
AMAP_KEY = "26d9ac20e8f589851bbd5b17c3d4cff4"

SITES_TO_FIX = [
    ("浚得兴_东莞鹏成码头", "东莞市麻涌镇鹏成码头", "广东", "东莞"),
    ("裕丰_广西名燕", "广西贵港市桂平市蒙圩镇名燕水泥", "广西", "贵港"),
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
        async with aiohttp.ClientSession() as session:
            for code, address, expect_prov, expect_city in SITES_TO_FIX:
                print(f"[{code}] {address}")
                result = await geocode_amap(session, address, expect_city)
                await asyncio.sleep(0.1)

                if result:
                    lng, lat = result["lng"], result["lat"]
                    print(f"  -> {lng:.6f}, {lat:.6f} | {result['province']} {result['city']} | {result['formatted']}")

                    await conn.execute(
                        "UPDATE repair_network_sites SET lng=$1, lat=$2, province=$3, city=$4 WHERE code=$5",
                        round(lng, 6), round(lat, 6), expect_prov, expect_city, code
                    )
                    print(f"  [UPDATED]")
                else:
                    print(f"  -> [FAILED]")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
