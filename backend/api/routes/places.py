"""
api/routes/places.py
GET /api/places/search — 景點搜尋（Google Places API）
GET /api/places/<place_id> — 景點詳細資料
"""

from flask import Blueprint, request, jsonify
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.places_service import search_places, get_place_detail

places_bp = Blueprint("places", __name__)


@places_bp.route("/search", methods=["GET"])
@require_auth
@swag_from("../swagger/places_search.yaml")
def search():
    """
    搜尋景點
    Query params: query (搜尋關鍵字), location (城市名或 lat,lng)
    """
    query    = request.args.get("query")
    location = request.args.get("location")

    if not query:
        return jsonify({"error": "缺少 query 參數"}), 400

    result = search_places(query=query, location=location)
    return jsonify(result), 200


@places_bp.route("/<place_id>", methods=["GET"])
@require_auth
@swag_from("../swagger/places_detail.yaml")
def place_detail(place_id):
    """
    取得景點詳細資料（評分、營業時間、票價、訂票連結）
    """
    result = get_place_detail(place_id=place_id)
    if not result:
        return jsonify({"error": "景點不存在"}), 404
    return jsonify(result), 200
