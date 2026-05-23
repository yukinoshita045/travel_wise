import os
import requests
from datetime import datetime
import pytz # 處理時區相減問題

import airportsdata
import pycountry

# 載入全球機場資料庫 (以 IATA 代碼為 Key)
AIRPORTS = airportsdata.load('IATA')

# 自訂名稱修正字典
COUNTRY_NAME_OVERRIDES = {
    "TW": "Taiwan",
    "US": "USA",
    "GB": "UK",
    "KR": "South Korea",
    "RU": "Russia"
}

def get_airport_details(iata_code: str) -> dict:
    """
    輸入機場縮寫 (如 NRT)，自動從全球開源庫回傳城市、國家與時區
    """
    if not iata_code:
        return {"city": "Unknown", "country": "Unknown", "timezone": "UTC"}

    iata_code = iata_code.upper()
    airport_info = AIRPORTS.get(iata_code)
    
    # 如果真的連全球資料庫都查不到，就只好退回預設值
    if not airport_info:
        return {"city": iata_code, "country": "Unknown", "timezone": "UTC"}
        
    country_code = airport_info.get("country", "")
    
    # 取得國家名稱：先看修正字典 -> 再查 pycountry -> 最後回傳代碼
    if country_code in COUNTRY_NAME_OVERRIDES:
        country_name = COUNTRY_NAME_OVERRIDES[country_code]
    else:
        country_obj = pycountry.countries.get(alpha_2=country_code)
        country_name = country_obj.name if country_obj else country_code

    return {
        "city": airport_info.get("city", iata_code),
        "country": country_name,
        "timezone": airport_info.get("tz", "UTC")
    }

# 機場縮寫與國家/城市對應
"""
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
"""

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

    # 直接讀取全球機場資料庫
    db_dep = get_airport_details(dep_code)
    db_arr = get_airport_details(arr_code)

    final_dep_country = db_dep["country"]
    final_arr_country = db_arr["country"]
    
    final_dep_city = db_dep["city"] if db_dep["city"] != dep_code else dep_data.get("airport", dep_code)
    final_arr_city = db_arr["city"] if db_arr["city"] != arr_code else arr_data.get("airport", arr_code)

    final_dep_tz = db_dep["timezone"] if db_dep["timezone"] != "UTC" else dep_data.get("timezone", "UTC")
    final_arr_tz = db_arr["timezone"] if db_arr["timezone"] != "UTC" else arr_data.get("timezone", "UTC")

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