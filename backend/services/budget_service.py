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
    if total_budget <= 0:
        total_budget = 0

    warnings     = []
    per_person   = round(total_budget / travelers, 2) if travelers else total_budget

    # 各類別分配額
    alloc = {k: round(total_budget * v, 2) for k, v in DEFAULT_RATIOS.items()}

    # 景點總票價
    spot_costs = []
    ticket_total = 0.0
    for s in spots:
        price = float(s.get("ticketPrice") or s.get("ticket_price") or 0)
        if price > 0:
            subtotal = price * travelers
            spot_costs.append({"name": s.get("name", ""), "pricePerPerson": price, "subtotal": subtotal})
            ticket_total += subtotal

    if ticket_total > alloc["activities"]:
        warnings.append(
            f"景點票價合計 {ticket_total:.0f} 超過活動預算 {alloc['activities']:.0f}，"
            "建議增加總預算或減少付費景點"
        )

    nights = max(days - 1, 1)

    breakdown = {
        "accommodation": {
            "total": alloc["accommodation"],
            "perPersonPerNight": round(alloc["accommodation"] / travelers / nights, 2) if travelers and nights else 0,
            "ratio": DEFAULT_RATIOS["accommodation"],
        },
        "food": {
            "total": alloc["food"],
            "perPersonPerDay": round(alloc["food"] / travelers / days, 2) if travelers and days else 0,
            "ratio": DEFAULT_RATIOS["food"],
        },
        "transport": {
            "total": alloc["transport"],
            "ratio": DEFAULT_RATIOS["transport"],
        },
        "activities": {
            "total": alloc["activities"],
            "spotCosts": spot_costs,
            "ticketTotal": ticket_total,
            "ratio": DEFAULT_RATIOS["activities"],
        },
        "emergency": {
            "total": alloc["emergency"],
            "ratio": DEFAULT_RATIOS["emergency"],
        },
    }

    is_over = ticket_total > alloc["activities"]

    return {
        "totalBudget":  total_budget,
        "currency":     currency,
        "perPerson":    per_person,
        "days":         days,
        "travelers":    travelers,
        "breakdown":    breakdown,
        "warnings":     warnings,
        "isOverBudget": is_over,
    }
