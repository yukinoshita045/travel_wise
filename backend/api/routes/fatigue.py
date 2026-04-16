"""
api/routes/fatigue.py
POST /api/fatigue/analyze — 飛行疲勞分析（SAFTE 模型）
"""

from flask import Blueprint, request, jsonify, g
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.fatigue_service import analyze_fatigue

fatigue_bp = Blueprint("fatigue", __name__)


@fatigue_bp.route("/analyze", methods=["POST"])
@require_auth
@swag_from("../swagger/fatigue.yaml")
def fatigue_analyze():
    """
    送入航班與旅行者資料，回傳疲勞指數與各因子解釋
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    # 必填欄位驗證
    required = ["departureTimezone", "arrivalTimezone", "flightDurationHours"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"缺少必填欄位: {missing}"}), 400

    result = analyze_fatigue(
        departure_tz       = data["departureTimezone"],
        arrival_tz         = data["arrivalTimezone"],
        flight_duration_hr = data["flightDurationHours"],
        layover_count      = data.get("layoverCount", 0),
        is_red_eye         = data.get("isRedEye", False),
        travelers          = data.get("travelers", []),   # [{"age": 65, "fitnessLevel": "low"}, ...]
    )
    return jsonify(result), 200
