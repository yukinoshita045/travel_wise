"""
api/routes/budget.py
POST /api/budget/calculate — 預算分配計算
"""

from flask import Blueprint, request, jsonify, g
from flasgger import swag_from
from utils.auth_middleware import require_auth
from services.budget_service import calculate_budget

budget_bp = Blueprint("budget", __name__)


@budget_bp.route("/calculate", methods=["POST"])
@require_auth
@swag_from("../swagger/budget.yaml")
def budget_calculate():
    """
    根據行程計算預算分配
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    required = ["totalBudget", "days", "travelers", "spots"]
    missing = [f for f in required if f not in data]
    if missing:
        return jsonify({"error": f"缺少必填欄位: {missing}"}), 400

    result = calculate_budget(
        total_budget = data["totalBudget"],
        days         = data["days"],
        travelers    = data["travelers"],
        spots        = data["spots"],
        currency     = data.get("currency", "TWD"),
    )
    return jsonify(result), 200
