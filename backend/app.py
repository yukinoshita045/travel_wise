"""
TravelWise Backend — Flask Application Entry Point
所有 Blueprint 在這裡集中註冊，Swagger UI 也在這裡掛載
"""

from flask import Flask
from flask_cors import CORS
from flasgger import Swagger

from config.database import init_db
from config.swagger_config import SWAGGER_CONFIG
from api.routes.chat import chat_bp
from api.routes.weather import weather_bp
from api.routes.fatigue import fatigue_bp
from api.routes.itinerary import itinerary_bp
from api.routes.places import places_bp
from api.routes.budget import budget_bp
from utils.error_handlers import register_error_handlers


def create_app():
    app = Flask(__name__)
    app.config["JSON_ENSURE_ASCII"] = False  # Flask 2.x
    app.json.ensure_ascii = False             # Flask 3.x

    # ── CORS（允許前端 localhost:5173 存取）──
    CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173", "https://your-production-domain.com"]}})

    # ── Swagger UI → http://localhost:5000/api/docs ──
    Swagger(app, config=SWAGGER_CONFIG)

    # ── MongoDB 連線初始化 ──
    init_db(app)

    # ── 註冊所有 API Blueprint ──
    app.register_blueprint(chat_bp,       url_prefix="/api/chat")
    app.register_blueprint(weather_bp,    url_prefix="/api/weather")
    app.register_blueprint(fatigue_bp,    url_prefix="/api/fatigue")
    app.register_blueprint(itinerary_bp,  url_prefix="/api/itinerary")
    app.register_blueprint(places_bp,     url_prefix="/api/places")
    app.register_blueprint(budget_bp,     url_prefix="/api/budget")

    # ── 統一錯誤處理 ──
    register_error_handlers(app)

    return app


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv()

    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=os.getenv("FLASK_DEBUG", "false").lower() == "true"
    )
