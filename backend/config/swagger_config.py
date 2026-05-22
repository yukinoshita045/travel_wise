"""
config/swagger_config.py
Flasgger（Swagger UI）全域設定
Swagger UI 網址：http://localhost:5000/api/docs
"""

SWAGGER_CONFIG = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/api/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs",
    "title": "TravelWise API",
    "uiversion": 3,
    "swagger_ui_bundle_js": "//unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js",
    "swagger_ui_standalone_preset_js": "//unpkg.com/swagger-ui-dist@5/swagger-ui-standalone-preset.js",
    "swagger_ui_css": "//unpkg.com/swagger-ui-dist@5/swagger-ui.css",
}

# OpenAPI 3.0 基本 Info（寫在 Swagger YAML 頂部）
SWAGGER_TEMPLATE = {
    "swagger": "2.0",
    "info": {
        "title": "TravelWise API",
        "description": """
## TravelWise 全齡化旅行適應決策支援平台 — 後端 API

### 功能模組
- `/api/chat`        AI 對話（GPT-4o 行程推薦）
- `/api/weather`     天氣查詢與衣物建議（Open-Meteo）
- `/api/fatigue`     飛行疲勞分析（SAFTE 模型）
- `/api/itinerary`   行程管理（CRUD + 推薦）
- `/api/places`      景點搜尋（Google Places）
- `/api/budget`      預算分配計算

### 認證方式
所有需要登入的 API 請在 Header 加上：
```
Authorization: Bearer <Firebase ID Token>
```
        """,
        "version": "1.0.0",
        "contact": {
            "name": "林鼎鈞",
            "email": "b11303045@ntu.edu.tw"
        }
    },
    "host": "localhost:5000",
    "basePath": "/",
    "schemes": ["http", "https"],
    "securityDefinitions": {
        "BearerAuth": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "Firebase ID Token，格式：Bearer <token>。開發測試可用：Bearer TEST_MODE"
        }
    },
    "security": [{"BearerAuth": []}],
    "consumes": ["application/json"],
    "produces": ["application/json"],
}
