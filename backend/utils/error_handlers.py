"""
utils/error_handlers.py
統一錯誤格式，仿照 LibreChat 的錯誤回應結構
所有 API 錯誤一律回傳 { "error": "...", "code": <HTTP status> }
"""

from flask import jsonify
import logging

logger = logging.getLogger(__name__)


def register_error_handlers(app):

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"error": str(e), "code": 400}), 400

    @app.errorhandler(401)
    def unauthorized(e):
        return jsonify({"error": "未授權，請先登入", "code": 401}), 401

    @app.errorhandler(403)
    def forbidden(e):
        return jsonify({"error": "權限不足", "code": 403}), 403

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "資源不存在", "code": 404}), 404

    @app.errorhandler(422)
    def unprocessable(e):
        return jsonify({"error": "請求參數格式錯誤", "code": 422}), 422

    @app.errorhandler(500)
    def internal_error(e):
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Internal Server Error: {e}\n{tb}")
        return jsonify({"error": str(e), "traceback": tb, "code": 500}), 500
