"""
services/currency_service.py
匯率換算服務 — 使用 Open Exchange Rates (免費無需 Key 的 API: exchangerate.host)
快取 1 小時，避免頻繁呼叫外部 API
"""

import requests
import logging
from utils.cache import get_cache, set_cache

logger = logging.getLogger(__name__)

# 支援的幣別清單
SUPPORTED_CURRENCIES = {
    "TWD": "新台幣",
    "USD": "美元",
    "JPY": "日圓",
    "EUR": "歐元",
    "GBP": "英鎊",
    "KRW": "韓圓",
    "HKD": "港幣",
    "SGD": "新加坡元",
    "AUD": "澳幣",
    "CNY": "人民幣",
    "THB": "泰銖",
}

EXCHANGE_RATE_API = "https://api.exchangerate-api.com/v4/latest/{base}"
CACHE_TTL = 3600  # 1小時


def get_exchange_rates(base: str = "TWD") -> dict:
    """
    取得以 base 為基準的所有匯率
    回傳 {"USD": 0.031, "JPY": 4.67, ...}
    優先從 Redis 快取讀取
    """
    base = base.upper()
    cache_key = f"exchange_rate:{base}"

    cached = get_cache(cache_key)
    if cached:
        return cached

    try:
        url = EXCHANGE_RATE_API.format(base=base)
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        data = resp.json()
        rates = data.get("rates", {})

        # 只保留支援的幣別
        filtered = {k: v for k, v in rates.items() if k in SUPPORTED_CURRENCIES}
        set_cache(cache_key, filtered, CACHE_TTL)
        return filtered

    except Exception as e:
        logger.error(f"[Currency] 匯率 API 失敗: {e}")
        # fallback: 固定匯率（2025年基準值）
        FALLBACK_FROM_TWD = {
            "TWD": 1.0,
            "USD": 0.031,
            "JPY": 4.67,
            "EUR": 0.029,
            "GBP": 0.025,
            "KRW": 41.8,
            "HKD": 0.243,
            "SGD": 0.042,
            "AUD": 0.048,
            "CNY": 0.225,
            "THB": 1.12,
        }
        if base == "TWD":
            return FALLBACK_FROM_TWD
        # 其他幣別 fallback：用 TWD fallback 反推
        if base in FALLBACK_FROM_TWD:
            base_rate = FALLBACK_FROM_TWD[base]
            return {k: round(v / base_rate, 4) for k, v in FALLBACK_FROM_TWD.items()}
        raise ValueError(f"不支援的幣別: {base}")


def convert_currency(amount: float, from_currency: str, to_currency: str) -> dict:
    """
    單一金額換算
    回傳 {"from": "TWD", "to": "JPY", "amount": 60000, "converted": 280200, "rate": 4.67}
    """
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"不支援的來源幣別: {from_currency}")
    if to_currency not in SUPPORTED_CURRENCIES:
        raise ValueError(f"不支援的目標幣別: {to_currency}")

    rates = get_exchange_rates(from_currency)
    rate = rates.get(to_currency)
    if rate is None:
        raise ValueError(f"無法取得 {from_currency} → {to_currency} 的匯率")

    converted = round(amount * rate, 2)
    return {
        "from": from_currency,
        "to": to_currency,
        "fromName": SUPPORTED_CURRENCIES[from_currency],
        "toName": SUPPORTED_CURRENCIES[to_currency],
        "amount": amount,
        "converted": converted,
        "rate": rate,
    }


def convert_budget_breakdown(breakdown: dict, from_currency: str, to_currency: str) -> dict:
    """
    將預算 breakdown 的所有金額欄位換算成目標幣別
    """
    rates = get_exchange_rates(from_currency)
    rate = rates.get(to_currency.upper())
    if rate is None:
        raise ValueError(f"無法取得匯率")

    def _convert(val):
        if isinstance(val, (int, float)):
            return round(val * rate, 2)
        if isinstance(val, dict):
            return {k: _convert(v) for k, v in val.items()}
        if isinstance(val, list):
            return [_convert(i) for i in val]
        return val

    return _convert(breakdown)
