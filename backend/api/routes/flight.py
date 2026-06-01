"""
api/routes/flight.py
GET /api/flight/info — 航班編號與日期自動帶入功能
"""

from flask import Blueprint, request, jsonify
from services.flight_service import fetch_flight_info
from utils.auth_middleware import require_auth

flight_bp = Blueprint("flight", __name__)

@flight_bp.route("/info", methods=["GET"])
@require_auth
def get_flight_info():
    """
    根據航班編號與出發日期查詢即時起降、航廈與機場國家資料
    使用情境：前端輸入航班號與日期後，調用此端點自動填入後續表單
    前端必須傳入：
    ?flightNum=IT203 (航班編號)
    &date=2026-12-25 (出發日期，格式 YYYY-MM-DD)
    """
    flight_num = request.args.get("flightNum")
    target_date = request.args.get("date") # 接收前端傳來的出發日期
    
    # 確定兩個參數都有給齊
    if not flight_num or not target_date:
        return jsonify({"error": "請提供完整的航班編號 (flightNum) 與 出發日期 (date)"}), 400
        
    try:
        # 將兩個參數都交給 Service 處理
        data = fetch_flight_info(flight_num, target_date)
        return jsonify(data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": f"航班系統查詢異常: {str(e)}"}), 500