"""
tests/conftest.py
pytest 共用 fixtures
"""

import pytest
from dotenv import load_dotenv

# 測試啟動時載入 .env，讓需要 app fixture 的整合測試能取得設定
load_dotenv()

from app import create_app


@pytest.fixture
def app():
    """建立測試用 Flask app"""
    app = create_app()
    app.config["TESTING"] = True
    yield app


@pytest.fixture
def client(app):
    """Flask 測試用 HTTP client"""
    return app.test_client()
