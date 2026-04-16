"""
tests/conftest.py
pytest 共用 fixtures
"""

import pytest
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
