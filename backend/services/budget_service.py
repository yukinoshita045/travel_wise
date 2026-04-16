"""
services/budget_service.py
預算分配計算服務
依照總預算、天數、人數、景點票價自動分配各項費用
"""


# ── 預算分配比例（可依實際需求調整）──
DEFAULT_RATIOS = {
    "accommodation": 0.35,   # 住宿 35%
    "food":          0.25,   # 餐費 25%
    "transport":     0.15,   # 交通 15%
    "activities":    0.20,   # 活動/景點 20%
    "emergency":     0.05,   # 緊急備用 5%
}


def calculate_budget(
    total_budget: float,
    days: int,
    travelers: int,
    spots: list,
    currency: str = "TWD",
) -> dict:
    """
    計算預算分配
    spots: [ { "name": "淺草寺", "ticketPrice": 0 }, ... ]
    Returns: {
        "totalBudget": 50000,
        "currency": "TWD",
        "perPerson": 25000,
        "breakdown": {
            "accommodation": { "total": 17500, "perPersonPerNight": 2500, "ratio": 0.35 },
            "food":          { "total": 12500, "perPersonPerDay": 1000, "ratio": 0.25 },
            "transport":     { "total": 7500, "ratio": 0.15 },
            "activities":    { "total": 10000, "spotCosts": [...], "ratio": 0.20 },
            "emergency":     { "total": 2500, "ratio": 0.05 }
        },
        "warnings": [],   # 超預算警告
        "isOverBudget": false
    }
    """
    # TODO:
    # 1. 計算景點總票價（spots 中所有 ticketPrice 加總 × travelers）
    # 2. 若景點費用超過 activities 分配額，發出 warning
    # 3. 計算各類別分配金額
    # 4. 計算每人每天各類費用
    # 5. 判斷是否超出預算
    raise NotImplementedError("budget_service 尚未實作")
