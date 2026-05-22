"""
api/routes/flight.py
GET /api/flight/info — 航班編號自動帶入功能
"""

from flask import Blueprint, request, jsonify
from services.flight_service import fetch_flight_info
from utils.auth_middleware import require_auth

flight_bp = Blueprint("flight", __name__)

@flight_bp.route("/info", methods=["GET"])
@require_auth
def get_flight_info():
    """
    根據航班編號查詢即時起降、日期與機場國家資料
    使用情境：前端輸入航班號後，調用此端點自動填入後續表單
    """
    flight_num = request.args.get("flightNum")
    if not flight_num:
        return jsonify({"error": "請提供航班編號參數 (flightNum)"}), 400
        
    try:
        # 呼叫服務獲取真實 API 數據
        data = fetch_flight_info(flight_num)
        return jsonify(data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"航班系統查詢異常: {str(e)}"}), 500