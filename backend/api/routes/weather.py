"""
api/routes/weather.py
GET /api/weather — 天氣查詢與衣物建議（Open-Meteo）
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.weather_service import get_weather_and_clothing

weather_bp = Blueprint("weather", __name__)


@weather_bp.route("", methods=["GET"])
@require_auth
@swag_from("../swagger/weather.yaml")
def weather():
    """
    查詢目的地天氣與衣物建議
    Query params: destination (城市名稱), date (YYYY-MM-DD)
    """
    destination = request.args.get("destination")
    date        = request.args.get("date")

    if not destination:
        return jsonify({"error": "缺少 destination 參數"}), 400

    result = get_weather_and_clothing(destination=destination, date=date)
    return jsonify(result), 200
