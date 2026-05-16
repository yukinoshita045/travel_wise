"""
api/routes/trip.py
POST /api/trip/plan — 一站式旅遊規劃端點（步驟 3~9）

使用者流程：
  步驟 3  輸入航班資料（出發/抵達城市、起降時間、轉機次數、是否補眠）
  步驟 4  後端驗證城市可辨識
  步驟 5  旅遊偏好（輕鬆休閒 / 觀光景點）
  步驟 6  AI 生成 Day by Day 行程
  步驟 7  後端自動計算疲勞分數、時差、年齡加權（已正式啟用）
  步驟 8  回傳時差適應指數、體力電池、建議活動開始時間、行程壓力類型
  步驟 9  前端顯示行程總覽，使用者確認後存入 DB（呼叫 /api/itinerary 存檔）
"""

from flask import Blueprint, request, jsonify, g
from utils.auth_middleware import require_auth
from services.places_service import search_spots
from services.itinerary_service import recommend_itinerary

import logging

logger = logging.getLogger(__name__)
trip_bp = Blueprint("trip", __name__)


# ── 城市白名單（快速驗證，可之後改成呼叫 OpenTripMap geoname）──
def _validate_city(city: str) -> bool:
    """步驟 4：驗證城市名稱可被識別（先用 search_spots 試查）"""
    try:
        result = search_spots(city=city, preferences=[], radius_m=1000, limit=1)
        return True  # 只要不拋例外就代表城市可識別
    except Exception:
        return False


# ── 疲勞計算 (正式版) ──────────────────────────────────────
def _compute_fatigue(flight_data: dict, travelers: list) -> dict:
    """
    步驟 7：疲勞分析
    呼叫 services.fatigue_service.analyze_fatigue 進行真實運算
    """
    from services.fatigue_service import analyze_fatigue
    import logging
    logger = logging.getLogger(__name__)

    try:
        # 將前端的 JSON 欄位對應到你的 analyze_fatigue 參數
        result = analyze_fatigue(
            departure_tz       = flight_data["departureTz"],
            arrival_tz         = flight_data["arrivalTz"],
            flight_duration_hr = float(flight_data["flightDurationHours"]),
            layover_count      = int(flight_data.get("layoverCount", 0)),
            is_red_eye         = bool(flight_data.get("isRedEye", False)),
            travelers          = travelers,
            has_napped         = bool(flight_data.get("hasNapped", False)), # 補眠參數
        )
        return result

    except Exception as e:
        logger.error(f"[Trip] 疲勞計算失敗: {e}")
        # 萬一運算過程發生預期外錯誤，回傳安全的預設值，避免整個行程生成中斷
        return {
            "baseScore":          50,
            "level":              "中等",
            "recoverHours":       6,
            "suggestedStartTime": "10:00",
            "tripStressType":     "一般行程",
            "jetLagIndex":        0,
            "energyBattery":      65,
            "explanation":        f"⚠️ 疲勞模組運算異常 ({str(e)})，目前顯示預估值。",
            "_placeholder":       True, # 前端可用此 flag 顯示提示訊息
        }


# ── 主端點 ────────────────────────────────────────────────────
@trip_bp.route("/plan", methods=["POST"])
@require_auth
def plan_trip():
    """
    一站式旅遊規劃（步驟 3~8）

    Request Body:
    {
        "flight": {
            "departureCity":    "Taipei",
            "arrivalCity":      "Tokyo",
            "departureTime":    "2026-06-01T08:00:00",
            "arrivalTime":      "2026-06-01T12:30:00",
            "departureTz":      "Asia/Taipei",
            "arrivalTz":        "Asia/Tokyo",
            "flightDurationHours": 3.5,
            "layoverCount":     0,
            "isRedEye":         false,
            "hasNapped":        true    
        },
        "travelers": [
            { "ageGroup": "adult", "fitnessLevel": "medium" }, 
            { "ageGroup": "senior", "fitnessLevel": "low" }
        ],
        "trip": {
            "days":          5,
            "budget":        80000,
            "travelStyle":   "觀光景點",
            "transportMode": "大眾運輸",
            "mustVisit":     ["淺草寺"]
        },
        "fatigueScore": 50    // 選填，若前端想強制覆蓋則帶入
    }

    Response (步驟 8):
    {
        "fatigue": { ... },          // 疲勞分析結果（步驟 8 顯示）
        "itinerary": { ... },        // AI 生成行程（步驟 9 顯示）
        "destination": "東京",
        "weather": null              // 預留，之後可加入天氣摘要
    }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    # ── 欄位驗證 ──────────────────────────────────────────────
    missing = [f for f in ["flight", "travelers", "trip"] if f not in data]
    if missing:
        return jsonify({"error": f"缺少必填欄位: {missing}"}), 400

    flight   = data["flight"]
    travelers = data["travelers"]
    trip     = data["trip"]

    if not flight.get("arrivalCity"):
        return jsonify({"error": "flight.arrivalCity 為必填"}), 400
    if not trip.get("days"):
        return jsonify({"error": "trip.days 為必填"}), 400

    destination = flight["arrivalCity"]

    # ── 步驟 4：城市驗證 ──────────────────────────────────────
    if not _validate_city(destination):
        return jsonify({
            "error": "無法識別目的地城市，請確認城市名稱（建議使用英文）",
            "field": "flight.arrivalCity"
        }), 422

    # ── 步驟 7：疲勞分析 ──────────────────────────────────────
    if "fatigueScore" in data:
        # 前端強制帶入時使用
        external_score = int(data["fatigueScore"])
        fatigue_result = _build_fatigue_from_score(external_score)
        logger.info(f"[Trip] 使用外部強制 fatigueScore={external_score}")
    else:
        # 正式進入 SAFTE 疲勞計算大腦
        fatigue_result = _compute_fatigue(flight, travelers)
        logger.info(f"[Trip] 計算出疲勞指數 baseScore={fatigue_result['baseScore']}")

    # ── 步驟 5/6：組成 tripParams 並呼叫 AI 生成行程 ──────────
    # 偏好映射：旅遊風格 → OpenTripMap 偏好標籤
    style_to_prefs = {
        "輕鬆休閒": ["自然", "美食", "購物"],
        "觀光景點": ["文化", "歷史", "宗教", "拍照"],
    }
    travel_style = trip.get("travelStyle", "觀光景點")
    preferences  = style_to_prefs.get(travel_style, ["文化", "美食"])

    trip_params = {
        "destination":       destination,
        "days":              trip["days"],
        "travelers":         len(travelers),
        "budget":            trip.get("budget", 0),
        "transportMode":     trip.get("transportMode", "大眾運輸"),
        "preferences":       preferences,
        "mustVisit":         trip.get("mustVisit", []),
        "fatigueContext": {
            "finalScore":   fatigue_result["baseScore"],
            "level":        fatigue_result["level"],
            "recoverHours": fatigue_result["recoverHours"],
        },
    }

    logger.info(f"[Trip] 開始規劃行程：{destination} {trip['days']}天，偏好={preferences}")
    itinerary_result = recommend_itinerary(
        user_uid=g.user["uid"],
        params=trip_params,
    )

    # ── 回傳步驟 8 + 9 所需資料 ──────────────────────────────
    return jsonify({
        "destination": destination,
        "fatigue":     fatigue_result,    # 步驟 8：疲勞分析顯示
        "itinerary":   itinerary_result,  # 步驟 9：行程總覽
        "weather":     None,              # 預留 — 可之後加入 get_weather_and_clothing
    }), 201


def _build_fatigue_from_score(score: int) -> dict:
    """
    當前端強制傳入 fatigueScore 時，由這裡補全其他展示欄位。
    """
    if score < 30:
        level, recover, battery, start_time, stress = "低", 4, 85, "09:00", "一般行程"
    elif score < 55:
        level, recover, battery, start_time, stress = "中等", 6, 65, "10:00", "一般行程"
    elif score < 75:
        level, recover, battery, start_time, stress = "高", 10, 45, "11:00", "高壓力行程"
    else:
        level, recover, battery, start_time, stress = "極高", 14, 25, "13:00", "高壓力行程"

    return {
        "baseScore":          score,
        "level":              level,
        "recoverHours":       recover,
        "suggestedStartTime": start_time,
        "tripStressType":     stress,
        "jetLagIndex":        round(score / 15),
        "energyBattery":      battery,
        "explanation":        f"疲勞指數 {score}，屬於{level}壓力，建議第一天活動從 {start_time} 開始。",
        "_placeholder":       False,
    }