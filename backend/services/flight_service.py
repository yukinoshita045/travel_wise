import os
import requests
from datetime import datetime
import pytz # 處理時區相減問題

# 機場縮寫與國家/城市對應
AIRPORT_DB = {
    "NRT": {"city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
    "HND": {"city": "Tokyo", "country": "Japan", "timezone": "Asia/Tokyo"},
    "KIX": {"city": "Osaka", "country": "Japan", "timezone": "Asia/Tokyo"},
    "NGO": {"city": "Nagoya", "country": "Japan", "timezone": "Asia/Tokyo"},
    "FUK": {"city": "Fukuoka", "country": "Japan", "timezone": "Asia/Tokyo"},
    "CTS": {"city": "Sapporo", "country": "Japan", "timezone": "Asia/Tokyo"},
    "TPE": {"city": "Taipei", "country": "Taiwan", "timezone": "Asia/Taipei"},
    "KHH": {"city": "Kaohsiung", "country": "Taiwan", "timezone": "Asia/Taipei"},
    "JFK": {"city": "New York", "country": "USA", "timezone": "America/New_York"},
    "LAX": {"city": "Los Angeles", "country": "USA", "timezone": "America/Los_Angeles"},
    "LHR": {"city": "London", "country": "UK", "timezone": "Europe/London"},
    "CDG": {"city": "Paris", "country": "France", "timezone": "Europe/Paris"},
    "SIN": {"city": "Singapore", "country": "Singapore", "timezone": "Asia/Singapore"},
    "HKG": {"city": "Hong Kong", "country": "Hong Kong", "timezone": "Asia/Hong_Kong"},
    "ICN": {"city": "Seoul", "country": "South Korea", "timezone": "Asia/Seoul"},
}

def fetch_flight_info(flight_number: str) -> dict:
    """
    呼叫 Aviationstack API 獲取真實航班資訊
    並將機場縮寫代碼轉換成國家、城市、時區與起降時間
    """
    api_key = os.getenv("AVIATIONSTACK_API_KEY")
    if not api_key:
        raise ValueError("系統設定中缺少 AVIATIONSTACK_API_KEY，請檢查 .env 檔案")

    flight_number = flight_number.upper().strip()
    
    # 呼叫 Aviationstack 航班查詢端點 (免費版限用 http)
    url = f"http://api.aviationstack.com/v1/flights?access_key={api_key}&flight_iata={flight_number}"
    
    try:
        response = requests.get(url, timeout=10)
        res_json = response.json()
    except Exception as e:
        raise RuntimeError(f"連線至航班外部 API 失敗: {str(e)}")

    # 驗證 API 回傳結果
    if "data" not in res_json or not res_json["data"]:
        raise ValueError(f"找不到航班編號 {flight_number} 的即時資訊，請確認編號是否正確")

    # 取得最新的一筆航班排程資料
    raw_flight = res_json["data"][0]
    
    dep_data = raw_flight.get("departure", {})
    arr_data = raw_flight.get("arrival", {})
    
    dep_code = dep_data.get("iata")
    arr_code = arr_data.get("iata")

    if not dep_code or not arr_code:
        raise ValueError(f"航班 {flight_number} 的起降機場代碼不完整，無法進行評估")

    # 直接讀取 DB 或 API 的預設值
    db_dep = AIRPORT_DB.get(dep_code, {})
    db_arr = AIRPORT_DB.get(arr_code, {})

    final_dep_country = db_dep.get("country") or dep_data.get("timezone", "Unknown").split("/")[0]
    final_arr_country = db_arr.get("country") or arr_data.get("timezone", "Unknown").split("/")[0]
    
    final_dep_city = db_dep.get("city") or dep_data.get("airport", dep_code)
    final_arr_city = db_arr.get("city") or arr_data.get("airport", arr_code)

    final_dep_tz = db_dep.get("timezone", dep_data.get("timezone", "UTC"))
    final_arr_tz = db_arr.get("timezone", arr_data.get("timezone", "UTC"))

    # 解析起降時間字串 (ISO 8601 格式處理)
    dep_time_str = dep_data.get("scheduled", "")
    arr_time_str = arr_data.get("scheduled", "")
    
    # 加入時區校正，算出真實飛行時間
    try:
        # 轉成 naive datetime
        dt_dep = datetime.strptime(dep_time_str[:19], "%Y-%m-%dT%H:%M:%S")
        dt_arr = datetime.strptime(arr_time_str[:19], "%Y-%m-%dT%H:%M:%S")
        
        # 賦予它們各自的時區，並統一轉成 UTC 來相減
        dep_utc = pytz.timezone(final_dep_tz).localize(dt_dep).astimezone(pytz.UTC)
        arr_utc = pytz.timezone(final_arr_tz).localize(dt_arr).astimezone(pytz.UTC)
        
        duration_hr = round(abs((arr_utc - dep_utc).total_seconds()) / 3600, 1)
        
        if duration_hr > 24 or duration_hr == 0: 
            duration_hr = 3.5
    except Exception:
        # 防呆：解析失敗則給定安全預設值
        duration_hr = 3.5

    return {
        "flightNumber": flight_number,
        "departure": {
            "code": dep_code,
            "city": final_dep_city,
            "country": final_dep_country,
            "timezone": final_dep_tz,
            "time": dep_time_str
        },
        "arrival": {
            "code": arr_code,
            "city": final_arr_city,
            "country": final_arr_country, 
            "timezone": final_arr_tz,
            "time": arr_time_str
        },
        "flightDurationHours": duration_hr
    }