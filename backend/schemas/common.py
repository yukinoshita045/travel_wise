"""
schemas/common.py
共用的 Pydantic 基底型別
"""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
