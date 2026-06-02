import asyncio
import asyncpg
import aiohttp

DB_URL = "postgresql://postgres:postgres@localhost:5432/cosco_gd"

# 手动推断每个网点的精确地址（城市 + 具体地点）
MANUAL_SITES = [
    # code, 搜索地址, 预期省份, 预期城市
    ("万年红_中山外运码头", "中山外运码头", "广东", "中山"),
    ("万建达_防城港万建达堆场", "防城港万建达堆场", "广西", "防城港"),
    ("万海通_东莞海腾码头", "东莞海腾码头", "广东", "东莞"),
    ("信步_北滘码头一期", "佛山顺德北滘码头", "广东", "佛山"),
    ("信步_揭阳红东码头", "揭阳红东码头", "广东", "揭阳"),
    ("信步_黄埔集司A场", "广州黄埔集司码头A场", "广东", "广州"),
    ("凯琪物流_昆明阳都", "昆明阳都物流", "云南", "昆明"),
    ("南宁亿邦_贺州堆场", "贺州堆场", "广西", "贺州"),
    ("南岗分公司_南岗堆场", "广州黄埔南岗堆场", "广东", "广州"),
    ("坚迅_乌冲口姬堂", "广州黄埔乌冲口姬堂", "广东", "广州"),
    ("坚迅_云浮港盛码头", "云浮港盛码头", "广东", "云浮"),
    ("坚迅_佛山南利", "佛山南利", "广东", "佛山"),
    ("坚迅_北滘码头二期", "佛山顺德北滘码头", "广东", "佛山"),
    ("广州弘运_乐平码头弘运", "佛山三水乐平码头", "广东", "佛山"),
    ("广州弘运_九江欧浦", "佛山南海九江欧浦", "广东", "佛山"),
    ("广州弘运_惠州堆场", "惠州堆场", "广东", "惠州"),
    ("广州弘运_梧州港", "梧州港", "广西", "梧州"),
    ("广州弘运_江门李锦记", "江门新会李锦记码头", "广东", "江门"),
    ("广州弘运_肇庆三榕", "肇庆三榕港", "广东", "肇庆"),
    ("弘运天浩_顺德颐德", "佛山顺德颐德", "广东", "佛山"),
    ("本港_肇庆三榕本港", "肇庆三榕港", "广东", "肇庆"),
    ("汕头裕港_蓝口铁路站点", "汕头蓝口铁路站点", "广东", "汕头"),
    ("泓洋_开平水口码头", "江门开平水口码头", "广东", "江门"),
    ("浚得兴_华津码头", "佛山高明华津码头", "广东", "佛山"),
    ("浚得兴_江门奔达码头", "江门奔达码头", "广东", "江门"),
    ("钦州弘运_防城港钦州弘运", "防城港钦州弘运", "广西", "防城港"),
]


async def geocode_nominatim(session, address):
    """使用Nominatim地理编码"""
    url = "https://nominatim.openstreetmap.org/search"
    params = {"q": f"中国 {address}", "format": "json", "limit": 1, "countrycodes": "cn"}
    headers = {"User-Agent": "COSCO-GD-CoordFix/1.0"}
    try:
        async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status == 200:
                data = await resp.json()
                if data:
                    return {"lng": float(data[0]["lon"]), "lat": float(data[0]["lat"])}
    except Exception:
        pass
    return None


async def main():
    conn = await asyncpg.connect(DB_URL)
    try:
        fixed = 0
        failed = []

        async with aiohttp.ClientSession() as session:
            for code, address, expect_prov, expect_city in MANUAL_SITES:
                print(f"[{code}] {address}")
                result = await geocode_nominatim(session, address)
                await asyncio.sleep(1.2)  # Nominatim限速

                if result:
                    lng, lat = result["lng"], result["lat"]
                    # 校验是否在合理范围内
                    if 18 <= lat <= 26 and 105 <= lng <= 118:
                        await conn.execute(
                            "UPDATE repair_network_sites SET lng=$1, lat=$2, province=$3, city=$4 WHERE code=$5",
                            round(lng, 6), round(lat, 6), expect_prov, expect_city, code
                        )
                        print(f"  -> {lng:.6f}, {lat:.6f} [OK]")
                        fixed += 1
                    else:
                        print(f"  -> {lng:.6f}, {lat:.6f} [OUT OF RANGE]")
                        failed.append(code)
                else:
                    print(f"  -> [FAILED]")
                    failed.append(code)

        print(f"\nDone: {fixed}/{len(MANUAL_SITES)} fixed")
        if failed:
            print(f"Failed: {failed}")

    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
