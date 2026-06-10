"""
services/weather_service.py
天氣服務 — 串接 Open-Meteo（免費，不需 API Key）
流程：城市名 → geocoding → 取得預報 → 計算體感溫度 → 生成衣物建議
"""

import os
import requests
from utils.cache import get_cache, set_cache

OPEN_METEO_BASE = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1")
GEO_BASE        = "https://geocoding-api.open-meteo.com/v1"

# Open-Meteo geocoding 用中文城市名常常查不到，這裡做中文→英文 fallback。
# 前端 toEnglishDestination 已轉部分城市，但台灣等城市會漏，後端再補一層保險。
_ZH_CITY = {
    "台北": "Taipei", "臺北": "Taipei", "台中": "Taichung", "臺中": "Taichung",
    "台南": "Tainan", "臺南": "Tainan", "高雄": "Kaohsiung", "新北": "New Taipei",
    "桃園": "Taoyuan", "台灣": "Taiwan", "臺灣": "Taiwan",
    "東京": "Tokyo", "大阪": "Osaka", "京都": "Kyoto", "札幌": "Sapporo",
    "福岡": "Fukuoka", "名古屋": "Nagoya", "沖繩": "Okinawa", "那霸": "Naha",
    "日本": "Japan", "首爾": "Seoul", "釜山": "Busan", "濟州": "Jeju", "韓國": "Korea",
    "曼谷": "Bangkok", "清邁": "Chiang Mai", "普吉": "Phuket", "泰國": "Thailand",
    "香港": "Hong Kong", "澳門": "Macau", "新加坡": "Singapore",
    "北京": "Beijing", "上海": "Shanghai", "廣州": "Guangzhou", "深圳": "Shenzhen",
    "倫敦": "London", "巴黎": "Paris", "羅馬": "Rome", "紐約": "New York",
    "洛杉磯": "Los Angeles", "舊金山": "San Francisco",
    "河內": "Hanoi", "胡志明": "Ho Chi Minh City", "吉隆坡": "Kuala Lumpur",
    "雪梨": "Sydney", "墨爾本": "Melbourne",
}


def _to_search_name(city: str) -> str:
    """把含中文的目的地轉成英文搜尋字（命中對應表就用英文，否則原樣回傳）"""
    for zh, en in _ZH_CITY.items():
        if zh in city:
            return en
    return city


def get_weather_and_clothing(destination: str, date: str | None = None) -> dict:
    """
    查詢目的地天氣與衣物建議
    Returns: {
        "destination": "Tokyo",
        "forecast": [ { "date": "...", "tempMax": 28, "tempMin": 18, "humidity": 70, "feelsLike": 30, "condition": "sunny" } ],
        "clothingSuggestion": "建議穿著短袖上衣搭配輕薄外套",
        "alerts": []
    }
    """
    cache_key = f"weather:{destination}:{date or 'today'}"
    cached = get_cache(cache_key)
    if cached:
        return cached

    # 1. Geocoding
    lat, lon, resolved_name = _geocode(destination)

    # 2. 取得 7 天預報
    forecast_url = (
        f"{OPEN_METEO_BASE}/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
        "weathercode,windspeed_10m_max"
        "&hourly=relativehumidity_2m"
        "&timezone=auto"
    )
    resp = requests.get(forecast_url, timeout=10)
    resp.raise_for_status()
    raw        = resp.json().get("daily", {})
    raw_hourly = resp.json().get("hourly", {})

    forecast = []
    alerts   = []
    hourly_humidity = raw_hourly.get("relativehumidity_2m", [])

    for i, dt in enumerate(raw.get("time", [])):
        t_max      = raw["temperature_2m_max"][i]
        t_min      = raw["temperature_2m_min"][i]
        wind_kmh   = raw["windspeed_10m_max"][i]
        precip_pct = raw["precipitation_probability_max"][i]
        wcode      = raw["weathercode"][i]

        # 取當天 24 小時的平均濕度（每天 24 筆）
        day_humidity = hourly_humidity[i*24:(i+1)*24]
        humidity = round(sum(day_humidity) / len(day_humidity), 1) if day_humidity else 60

        feels = _feels_like(t_max, humidity, wind_kmh)
        cond  = _wmo_to_condition(wcode)

        if precip_pct >= 70:
            alerts.append({"date": dt, "message": f"{dt} 降雨機率 {precip_pct}%，請攜帶雨具"})

        forecast.append({
            "date":       dt,
            "tempMax":    t_max,
            "tempMin":    t_min,
            "humidity":   humidity,
            "windKmh":    wind_kmh,
            "feelsLike":  round(feels, 1),
            "condition":  cond,
            "precipProb": precip_pct,
        })

    avg_feel = sum(f["feelsLike"] for f in forecast) / len(forecast) if forecast else 20
    clothing  = _clothing_suggestion(avg_feel, any(a for a in alerts))

    result = {
        "destination":       resolved_name,
        "forecast":          forecast,
        "clothingSuggestion": clothing,
        "alerts":            alerts,
    }
    set_cache(cache_key, result, ttl_seconds=3600)   # 快取 1 小時
    return result


def _geocode(city: str) -> tuple[float, float, str]:
    """Open-Meteo geocoding → (lat, lon, name)。中文城市先轉英文再查，較不會查無。"""
    # 先用（可能轉英文後的）名稱查，查不到再用原始字串試一次
    candidates = []
    search = _to_search_name(city)
    candidates.append(search)
    if city != search:
        candidates.append(city)

    for name in candidates:
        url  = f"{GEO_BASE}/search?name={name}&count=1&language=zh&format=json"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])
        if results:
            r = results[0]
            return r["latitude"], r["longitude"], r.get("name", city)

    raise ValueError(f"找不到城市：{city}")


def _feels_like(temp_c: float, humidity: float, wind_kmh: float) -> float:
    """
    體感溫度：
    - temp > 27°C → Heat Index 公式 (Rothfusz)
    - temp < 10°C → Wind Chill 公式
    - 其他       → 原始溫度
    """
    T = temp_c
    R = humidity
    V = wind_kmh

    if T > 27:
        HI = (
            -8.78469475556
            + 1.61139411 * T
            + 2.33854883889 * R
            - 0.14611605 * T * R
            - 0.012308094 * T ** 2
            - 0.0164248277778 * R ** 2
            + 0.002211732 * T ** 2 * R
            + 0.00072546 * T * R ** 2
            - 0.000003582 * T ** 2 * R ** 2
        )
        return HI
    elif T < 10 and V > 4.8:
        WC = 13.12 + 0.6215 * T - 11.37 * V ** 0.16 + 0.3965 * T * V ** 0.16
        return WC
    else:
        return T


def _wmo_to_condition(code: int) -> str:
    """WMO weathercode → 中文狀況"""
    if code == 0:
        return "晴天"
    elif code in (1, 2, 3):
        return "多雲"
    elif code in range(45, 50):
        return "霧"
    elif code in range(51, 68):
        return "雨"
    elif code in range(71, 78):
        return "雪"
    elif code in range(80, 83):
        return "陣雨"
    elif code in range(95, 100):
        return "雷雨"
    return "未知"


def _clothing_suggestion(avg_feels: float, has_rain: bool) -> str:
    """依平均體感溫度生成衣物建議"""
    if avg_feels >= 32:
        base = "天氣炎熱，建議穿著輕薄透氣的短袖短褲，並注意防曬（帽子、防曬乳）"
    elif avg_feels >= 25:
        base = "氣溫舒適偏暖，建議穿著短袖搭配薄外套，早晚稍涼可備一件薄長袖"
    elif avg_feels >= 15:
        base = "氣溫涼爽，建議穿著長袖搭配薄外套或針織上衣"
    elif avg_feels >= 5:
        base = "天氣較冷，建議穿著厚外套或毛衣，搭配圍巾手套"
    else:
        base = "氣溫極低，建議穿著羽絨外套並做好全身保暖，注意防滑"

    if has_rain:
        base += "；預報有降雨，請務必攜帶雨傘或雨衣"

    return base
