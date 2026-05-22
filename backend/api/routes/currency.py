"""
api/routes/currency.py
GET  /api/currency/rates   — 取得匯率列表
POST /api/currency/convert — 金額換算
"""

from flask import Blueprint, request, jsonify
from services.currency_service import (
    get_exchange_rates,
    convert_currency,
    SUPPORTED_CURRENCIES,
)

currency_bp = Blueprint("currency", __name__)


@currency_bp.route("/rates", methods=["GET"])
def get_rates():
    """
    取得以指定幣別為基準的匯率列表
    Query: ?base=TWD (預設 TWD)
    Response:
      {
        "base": "TWD",
        "rates": {"JPY": 4.67, "USD": 0.031, ...},
        "supportedCurrencies": {"TWD": "新台幣", ...}
      }
    """
    base = request.args.get("base", "TWD").upper()
    if base not in SUPPORTED_CURRENCIES:
        return jsonify({"error": f"不支援的幣別: {base}，支援：{list(SUPPORTED_CURRENCIES.keys())}"}), 400

    try:
        rates = get_exchange_rates(base)
        return jsonify({
            "base": base,
            "baseName": SUPPORTED_CURRENCIES[base],
            "rates": rates,
            "supportedCurrencies": SUPPORTED_CURRENCIES,
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@currency_bp.route("/convert", methods=["POST"])
def convert():
    """
    金額換算
    Body: {"amount": 60000, "from": "TWD", "to": "JPY"}
    Response:
      {
        "from": "TWD", "to": "JPY",
        "amount": 60000, "converted": 280200, "rate": 4.67,
        "fromName": "新台幣", "toName": "日圓"
      }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "缺少請求 body"}), 400

    missing = [f for f in ["amount", "from", "to"] if f not in data]
    if missing:
        return jsonify({"error": f"缺少必填欄位: {missing}"}), 400

    try:
        amount = float(data["amount"])
        if amount < 0:
            return jsonify({"error": "金額不能為負數"}), 400

        result = convert_currency(amount, data["from"], data["to"])
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"換算失敗: {str(e)}"}), 500
