import os
import requests
from datetime import datetime
import pytz 

import airportsdata
import pycountry

# 載入全球機場資料庫 (以 IATA 代碼為 Key)
AIRPORTS = airportsdata.load('IATA')

# 自訂國家名稱修正字典
COUNTRY_NAME_OVERRIDES = {
    "TW": "Taiwan", "US": "USA", "GB": "UK",
    "KR": "South Korea", "RU": "Russia"
}

# 常見航空公司代碼對應表
COMMON_AIRLINES = {
    "BR": "EVA Air", "CI": "China Airlines", "JX": "STARLUX Airlines",
    "IT": "Tigerair Taiwan", "AE": "Mandarin Airlines", "B7": "UNI Air",
    "CX": "Cathay Pacific", "JL": "Japan Airlines", "NH": "All Nippon Airways",
    "AY": "Finnair", "EK": "Emirates", "SQ": "Singapore Airlines"
}

def get_airport_details(iata_code: str) -> dict:
    """從全球開源庫回傳城市、國家與時區"""
    if not iata_code:
        return {"city": "Unknown", "country": "Unknown", "timezone": "UTC"}

    iata_code = iata_code.upper()
    airport_info = AIRPORTS.get(iata_code)
    
    if not airport_info:
        return {"city": iata_code, "country": "Unknown", "timezone": "UTC"}
        
    country_code = airport_info.get("country", "")
    
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

def fetch_flight_info(flight_input: str, target_date: str) -> dict:
    """呼叫 AeroDataBox API 獲取未來航班精準資訊"""
    rapidapi_key = os.getenv("RAPIDAPI_KEY")
    if not rapidapi_key:
        raise ValueError("系統設定中缺少 RAPIDAPI_KEY，請檢查 .env 檔案")

    flight_input = flight_input.upper().strip()

    # 呼叫 AeroDataBox
    url = f"https://aerodatabox.p.rapidapi.com/flights/number/{flight_input}/{target_date}"
    headers = {
        "X-RapidAPI-Key": rapidapi_key,
        "X-RapidAPI-Host": "aerodatabox.p.rapidapi.com"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 404:
            raise ValueError(f"查無 {target_date} 出發的 {flight_input} 航班排程，請確認班表是否正確")
        response.raise_for_status()
        res_json = response.json()
    except Exception as e:
        if isinstance(e, ValueError):
            raise e
        raise RuntimeError(f"連線至外部航班系統失敗: {str(e)}")

    if not res_json or not isinstance(res_json, list):
        raise ValueError(f"查無 {target_date} 出發的 {flight_input} 航班排程資料")

    flight_data = res_json[0]

    dep_data = flight_data.get("departure", {})
    arr_data = flight_data.get("arrival", {})

    dep_code = dep_data.get("airport", {}).get("iata")
    arr_code = arr_data.get("airport", {}).get("iata")

    if not dep_code or not arr_code:
        raise ValueError(f"航班 {flight_input} 的起降機場代碼不完整")

    db_dep = get_airport_details(dep_code)
    db_arr = get_airport_details(arr_code)

    dep_terminal = dep_data.get("terminal") or "尚未提供"
    dep_gate = dep_data.get("gate") or "尚未提供"
    arr_terminal = arr_data.get("terminal") or "尚未提供"
    arr_gate = arr_data.get("gate") or "尚未提供"

    def extract_time(data_dict, fallback_date):
        # 1. 尋找直接的字串欄位
        raw_time = (
            data_dict.get("scheduledTimeLocal") or 
            data_dict.get("actualTimeLocal") or 
            data_dict.get("scheduledTimeUtc")
        )
        # 2. 如果沒有，尋找藏在巢狀字典裡的欄位
        if not raw_time and "scheduledTime" in data_dict and isinstance(data_dict["scheduledTime"], dict):
            raw_time = data_dict["scheduledTime"].get("local") or data_dict["scheduledTime"].get("utc")
            
        # 3. 如果還是抓不到，啟用防呆
        if not raw_time:
            return f"{fallback_date}T00:00:00"
            
        # 4. 統一字串格式 (切掉尾部時區，並確保擁有秒數)
        clean_time = raw_time.replace(" ", "T")
        if len(clean_time) >= 16:
            return clean_time[:16] + ":00" # 強制將 YYYY-MM-DDTHH:MM 補上 :00
        return f"{fallback_date}T00:00:00"

    dep_time_str = extract_time(dep_data, target_date)
    arr_time_str = extract_time(arr_data, target_date)

    # 時區校正與真實飛行時間計算
    try:
        dt_dep = datetime.strptime(dep_time_str, "%Y-%m-%dT%H:%M:%S")
        dt_arr = datetime.strptime(arr_time_str, "%Y-%m-%dT%H:%M:%S")
        
        dep_utc = pytz.timezone(db_dep["timezone"]).localize(dt_dep).astimezone(pytz.UTC)
        arr_utc = pytz.timezone(db_arr["timezone"]).localize(dt_arr).astimezone(pytz.UTC)
        
        duration_hr = round(abs((arr_utc - dep_utc).total_seconds()) / 3600, 1)
        if duration_hr > 24 or duration_hr == 0: 
            duration_hr = 3.5
    except Exception:
        duration_hr = 3.5

    api_airline_name = flight_data.get("airline", {}).get("name")
    airline_name = api_airline_name or COMMON_AIRLINES.get(flight_input[:2], "尚未提供")

    return {
        "flightNumber": flight_input,
        "airline": airline_name,
        "departure": {
            "code": dep_code,
            "city": db_dep["city"],
            "country": db_dep["country"],
            "timezone": db_dep["timezone"],
            "terminal": dep_terminal,
            "gate": dep_gate,
            "time": dep_time_str
        },
        "arrival": {
            "code": arr_code,
            "city": db_arr["city"],
            "country": db_arr["country"], 
            "timezone": db_arr["timezone"],
            "terminal": arr_terminal,
            "gate": arr_gate,
            "time": arr_time_str
        },
        "flightDurationHours": duration_hr
    }