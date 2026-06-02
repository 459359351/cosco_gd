import asyncio
import asyncpg
import aiohttp
import json

DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"
AMAP_KEY = "26d9ac20e8f589851bbd5b17c3d4cff4"

# 需要修正的网点: (code, 搜索地址, 省份, 城市)
SITES_TO_FIX = [
    # 零坐标
    ("浚得兴_华津码头", "佛山市高明区华津码头", "广东", "佛山"),

    # 省份/城市错误
    ("珠三角运营中心_佛山南鲲", "佛山市南海区南鲲码头", "广东", "佛山"),
    ("弘运天浩_莲花山", "广州市番禺区莲花山港", "广东", "广州"),
    ("本港_炭步新港", "广州市花都区炭步镇", "广东", "广州"),
    ("深圳运营中心_汕头国集", "汕头港国际集装箱码头", "广东", "汕头"),
    ("深圳运营中心_汕头堆场", "汕头港集装箱堆场", "广东", "汕头"),
    ("深圳运营中心_汕头广澳", "汕头广澳港区", "广东", "汕头"),
    ("北部湾运营中心_防城港外堆场", "防城港外堆场", "广西", "防城港"),
    ("北部湾运营中心_防城港二堆场", "防城港第二堆场", "广西", "防城港"),
    ("北部湾运营中心_广西钦州港自营", "钦州港", "广西", "钦州"),
    ("南宁亿邦_广西梧州赤水港", "梧州赤水港", "广西", "梧州"),
    ("广州运营中心_惠州龙溪", "惠州市博罗县龙溪镇", "广东", "惠州"),
    ("广州运营中心_虎门一期", "东莞市虎门港", "广东", "东莞"),
    ("广州弘运_三水新港", "佛山市三水区三水新港", "广东", "佛山"),
    ("广州弘运_东莞石龙", "东莞市石龙镇石龙港", "广东", "东莞"),
    ("广州弘运_江门天马港", "江门市新会区天马港", "广东", "江门"),
    ("广州弘运_新会亚太", "江门市新会区亚太纸业", "广东", "江门"),
    ("广州弘运_新会新港", "江门市新会区新会港", "广东", "江门"),
    ("浚得兴_东莞鹏成码头", "东莞市鹏成码头", "广东", "东莞"),
    ("珠三角运营中心_贵阳陆港铁路场", "贵阳市陆港型国家物流枢纽", "贵州", "贵阳"),
    ("裕丰_广西名燕", "南宁市名燕特种水泥", "广西", "南宁"),
    ("深圳运营中心_深圳大铲湾", "深圳市大铲湾码头", "广东", "深圳"),

    # 共享坐标需要分开的
    ("广州运营中心_淡水河码头", "广州市增城区新塘镇淡水河码头", "广东", "广州"),
    ("广州运营中心_新沙港", "东莞市麻涌镇新沙港", "广东", "东莞"),
    ("广州运营中心_虎门二期码头", "东莞市虎门港", "广东", "东莞"),
    ("广州运营中心_虎门三期码头", "东莞市虎门港", "广东", "东莞"),
]


async def geocode_amap(session, address, city_hint):
    """使用高德地理编码API"""
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
                await asyncio.sleep(0.1)  # 高德限速

                if result:
                    lng, lat = result["lng"], result["lat"]
                    # 校验省份/城市是否匹配
                    actual_prov = result["province"]
                    actual_city = result["city"]
                    prov_ok = expect_prov in actual_prov or actual_prov in expect_prov
                    city_ok = expect_city in actual_city or actual_city in expect_city or (expect_city == "东莞" and "东莞" in actual_city) or (expect_city == "中山" and "中山" in actual_city)

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

        # 保存结果到JSON
        with open("geocode_results.json", "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # 更新数据库（只更新成功的）
        fixed = 0
        for r in results:
            if not r.get("failed"):
                await conn.execute(
                    "UPDATE repair_network_sites SET lng=$1, lat=$2, province=$3, city=$4 WHERE code=$5",
                    round(r["lng"], 6), round(r["lat"], 6), r["province"], r["city"], r["code"]
                )
                fixed += 1

        print(f"\n完成: {fixed}/{len(SITES_TO_FIX)} 个网点已更新")

        # 显示有警告的
        warnings = [r for r in results if not r.get("failed") and (not r.get("prov_ok") or not r.get("city_ok"))]
        if warnings:
            print(f"\n有警告的网点 ({len(warnings)} 个):")
            for w in warnings:
                print(f"  {w['code']}: 期望 {w['province']}/{w['city']}, 实际 {w['actual_province']}/{w['actual_city']}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
