from datetime import date, timedelta


def mock_yards() -> list[dict]:
    return [
        {
            "id": 1,
            "name": "南沙港堆场A",
            "code": "GD-NSA-001",
            "yard_type": "yard",
            "province": "广东",
            "city": "广州",
            "lng": 113.6318,
            "lat": 22.7714,
            "capacity": 15000,
            "status": "normal",
        },
        {
            "id": 2,
            "name": "深圳盐田物流点",
            "code": "GD-SZ-002",
            "yard_type": "logistics",
            "province": "广东",
            "city": "深圳",
            "lng": 114.2580,
            "lat": 22.5860,
            "capacity": 12000,
            "status": "busy",
        },
        {
            "id": 3,
            "name": "钦州保税堆场",
            "code": "GX-QZ-001",
            "yard_type": "yard",
            "province": "广西",
            "city": "钦州",
            "lng": 108.6131,
            "lat": 21.9589,
            "capacity": 9000,
            "status": "warning",
        },
    ]


def mock_trend(days: int = 7) -> list[dict]:
    today = date.today()
    points: list[dict] = []
    for idx in range(days):
        day = today - timedelta(days=days - idx - 1)
        points.append(
            {
                "date": day.isoformat(),
                "in_teu": 260 + idx * 8,
                "out_teu": 240 + idx * 6,
                "stock_teu": 3800 + idx * 40,
            }
        )
    return points


def mock_cargo_distribution() -> list[dict]:
    return [
        {"category": "矿石", "volume": 4200},
        {"category": "煤炭", "volume": 3200},
        {"category": "粮食", "volume": 1500},
        {"category": "机械", "volume": 1200},
        {"category": "其他", "volume": 780},
    ]


def mock_alerts() -> list[dict]:
    return [
        {
            "id": 101,
            "yard_id": 2,
            "level": "high",
            "alert_type": "拥堵",
            "message": "深圳盐田物流点在场车辆超过阈值",
            "created_at": "2026-05-16T17:30:00",
        },
        {
            "id": 102,
            "yard_id": 3,
            "level": "medium",
            "alert_type": "库存",
            "message": "钦州保税堆场库存接近90%",
            "created_at": "2026-05-16T17:50:00",
        },
    ]


def mock_flow() -> list[dict]:
    """OD 示例：前端只渲染「起点、终点堆场 code 均出现在当前 yards 列表中」的边。"""
    return [
        {"from_code": "GD-NSA-001", "to_code": "GD-SZ-002", "value": 360},
        {"from_code": "GD-NSA-001", "to_code": "GX-QZ-001", "value": 220},
        {"from_code": "GD-SZ-002", "to_code": "GX-QZ-001", "value": 170},
        # 广西省内（与 seed_gd_gx 中 code 一致；筛选「广西」时仍可看到飞线）
        {"from_code": "GX-QZ-001", "to_code": "GX-BH-001", "value": 140},
        {"from_code": "GX-NN-001", "to_code": "GX-FCG-001", "value": 110},
        {"from_code": "GX-BH-001", "to_code": "GX-NN-001", "value": 85},
    ]
