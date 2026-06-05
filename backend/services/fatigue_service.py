import pytz
from datetime import datetime


# 疲勞因子權重常數
WEIGHTS = {
    "per_timezone_crossed":     3.0,   # 每跨越 1 個時區 +3 分
    "per_hour_flight":          1.5,   # 每小時飛行 +1.5 分
    "per_layover":             15.0,   # 每次轉機 +15 分
    "red_eye_penalty":         20.0,   # 紅眼航班 +20 分
    "nap_recovery":            -5.0,   # 補眠恢復 -5 分
}


# 旅行者疲勞衰減係數（依年齡與運動習慣）
TRAVELER_MULTIPLIERS = {
    ("young", "high"):   0.7,   # 年輕 + 高運動量
    ("young", "medium"): 0.8,
    ("young", "low"):    1.0,
    ("adult", "high"):   0.8,   # 擴充 adult 以防前端傳入
    ("adult", "medium"): 1.0,
    ("adult", "low"):    1.2,
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
    has_napped: bool = False,
) -> dict:
    try:
        # 1. 計算時區差距（用 pytz 解析）
        now = datetime.now()
        tz_dep = pytz.timezone(departure_tz).localize(now).utcoffset().total_seconds() / 3600
        tz_arr = pytz.timezone(arrival_tz).localize(now).utcoffset().total_seconds() / 3600
        tz_diff = abs(tz_arr - tz_dep)


        # 2. 依 WEIGHTS 計算各因子分數
        timezone_score = tz_diff * WEIGHTS["per_timezone_crossed"]
        flight_score = flight_duration_hr * WEIGHTS["per_hour_flight"]
        layover_score = layover_count * WEIGHTS["per_layover"]
        red_eye_score = WEIGHTS["red_eye_penalty"] if is_red_eye else 0


        # 3. 加總為 raw_base_score，並處理補眠扣抵
        raw_base_score = timezone_score + flight_score + layover_score + red_eye_score
        if has_napped:
            raw_base_score = max(0, raw_base_score + WEIGHTS["nap_recovery"])


        # 4. 對每位旅行者套用 multiplier，計算 final_score
        processed_travelers = []
        max_final_score = 0
       
        for idx, t in enumerate(travelers):
            age = t.get("ageGroup", "adult")
            fitness = t.get("fitnessLevel", "medium")
            # 取得對應倍率，找不到則預設 1.0
            multiplier = TRAVELER_MULTIPLIERS.get((age, fitness), 1.0)
            final_score = min(raw_base_score * multiplier, MAX_SCORE)
           
            # 找出整團人中最累的分數，作為行程建議基準
            if final_score > max_final_score:
                max_final_score = final_score


            processed_travelers.append({
                "index": idx,
                "multiplier": multiplier,
                "finalScore": int(final_score)
            })


        # 5. 依分數決定等級與建議恢復時間
        representative_score = int(max_final_score if processed_travelers else raw_base_score)
        level, recover, battery, start_time, stress = _get_level(representative_score)


        # 若有補眠，額外回充 15% 體力電池
        if has_napped:
            battery = min(100, battery + 15)


        # 6. 生成可讀的解釋文字
        explanations = [
            f"跨越 {int(tz_diff)} 個時區，對生物鐘產生偏移，貢獻 {int(timezone_score)} 分",
            f"飛行 {round(flight_duration_hr, 1)} 小時，貢獻 {int(flight_score)} 分"
        ]
        if layover_count > 0:
            explanations.append(f"轉機 {layover_count} 次，增加疲勞 {int(layover_score)} 分")
        if is_red_eye:
            explanations.append(f"紅眼航班導致睡眠品質下降，增加 {int(red_eye_score)} 分")
        if has_napped:
            explanations.append(f"偵測到已進行補眠，有效恢復 {battery}% 體力電池並降低疲勞指數")


        return {
            "baseScore": representative_score,
            "level": level,
            "energyBattery": battery,
            "jetLagIndex": int(tz_diff),
            "suggestedStartTime": start_time,
            "tripStressType": stress,
            "recoverHours": recover,
            "explanation": "；".join(explanations) + f"。綜合評估為{level}壓力。",
            "_placeholder": False,
           
            "travelers": processed_travelers,
            "breakdown": {
                "timezoneCrossed": int(tz_diff),
                "timezoneScore": int(timezone_score),
                "flightScore": int(flight_score),
                "layoverScore": int(layover_score),
                "redEyeScore": int(red_eye_score)
            },
            "explanations": explanations
        }


    except Exception as e:
        # 防呆：報錯時回傳 Placeholder 50
        return {
            "baseScore": 50, "level": "中等", "energyBattery": 65, "jetLagIndex": 0,
            "suggestedStartTime": "10:00", "tripStressType": "一般行程", "recoverHours": 6,
            "explanation": f"疲勞計算暫時無法使用 ({str(e)})", "_placeholder": True
        }




def _get_low_level_battery(score: float) -> int:
    """
    短程 / 低分數時，依分數在低區間的相對位置呈現差異化電池值。
    score 0-30 映射到 85-65（原低等級的 85 為基準，逐步降低）
    """
    battery = 85 - int(score * 0.67)
    return max(65, battery)




def _get_level(score: float) -> tuple:
    """
    依分數回傳（等級文字, 建議恢復小時數, 電池趴數, 建議開始時間, 行程類型）
    """
    if score >= 75:
        return ("極高", 24, 25, "13:00", "高壓力行程")
    elif score >= 55:
        return ("高", 12, 45, "11:00", "高壓力行程")
    elif score >= 30:
        return ("中等", 6, 65, "10:00", "一般行程")
    else:
        return ("低", 4, _get_low_level_battery(score), "09:00", "一般行程")