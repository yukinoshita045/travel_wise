"""
services/fatigue_service.py
飛行疲勞分析 — 仿 SAFTE（Sleep, Activity, Fatigue, Task Effectiveness）模型
計算各因子的疲勞分數並提供可解釋性輸出
"""


# ── 疲勞因子權重常數 ──
WEIGHTS = {
    "per_timezone_crossed":     3.0,   # 每跨越 1 個時區 +3 分
    "per_hour_flight":          1.5,   # 每小時飛行 +1.5 分
    "per_layover":             15.0,   # 每次轉機 +15 分
    "red_eye_penalty":         20.0,   # 紅眼航班 +20 分
}

# ── 旅行者疲勞衰減係數（依年齡與運動習慣）──
TRAVELER_MULTIPLIERS = {
    ("young", "high"):   0.7,   # 年輕 + 高運動量
    ("young", "medium"): 0.8,
    ("young", "low"):    1.0,
    ("senior", "high"):  1.0,
    ("senior", "medium"): 1.2,
    ("senior", "low"):   1.5,   # 高齡 + 無運動習慣（最高負擔）
}

MAX_SCORE = 100


def analyze_fatigue(
    departure_tz: str,
    arrival_tz: str,
    flight_duration_hr: float,
    layover_count: int = 0,
    is_red_eye: bool = False,
    travelers: list = [],
) -> dict:
    """
    計算疲勞指數
    Returns: {
        "baseScore": 45,
        "travelers": [
            { "index": 0, "multiplier": 1.2, "finalScore": 54, "level": "中等", "recoverHours": 8 }
        ],
        "breakdown": {
            "timezoneCrossed": 8,
            "timezoneScore": 24,
            "flightScore": 18,
            "layoverScore": 15,
            "redEyeScore": 20
        },
        "explanations": [
            "跨越 8 個時區，對生物鐘偏移量較大，貢獻 24 分",
            "轉機 1 次，增加疲勞 15 分",
            "紅眼航班，睡眠品質下降，增加 20 分"
        ]
    }
    """
    # TODO:
    # 1. 計算時區差距（用 pytz 或 zoneinfo 解析 departure_tz / arrival_tz）
    # 2. 依 WEIGHTS 計算各因子分數
    # 3. 加總為 base_score（最大 MAX_SCORE）
    # 4. 對每位旅行者套用 multiplier，計算 final_score
    # 5. 依分數決定等級（低/中等/高/極高）與建議恢復時間
    # 6. 生成人類可讀的解釋文字列表
    raise NotImplementedError("fatigue_service 尚未實作")


def _get_level(score: float) -> tuple[str, int]:
    """
    依分數回傳（等級文字, 建議恢復小時數）
    TODO: 實作分級邏輯
    """
    raise NotImplementedError
