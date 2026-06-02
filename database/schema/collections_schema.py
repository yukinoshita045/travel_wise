"""
database/schema/README.md 說明檔案
以下用 Python dict 格式描述各 MongoDB Collection 的欄位結構
"""

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Collection: users
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USER_SCHEMA = {
    "uid":         "str  — Firebase UID（主要索引）",
    "email":       "str",
    "displayName": "str",
    "createdAt":   "datetime (UTC)",
    "updatedAt":   "datetime (UTC)",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Collection: conversations
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONVERSATION_SCHEMA = {
    "conversationId": "str UUID（主要索引）",
    "userId":         "str — 關聯 users.uid（索引）",
    "title":          "str",
    "createdAt":      "datetime (UTC)",
    "updatedAt":      "datetime (UTC)",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Collection: messages
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MESSAGE_SCHEMA = {
    "messageId":      "str UUID",
    "conversationId": "str — 關聯 conversations.conversationId（索引）",
    "userId":         "str — 關聯 users.uid（索引）",
    "role":           "str — 'user' | 'assistant'",
    "content":        "str — 訊息內容",
    "createdAt":      "datetime (UTC)",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Collection: itineraries
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ITINERARY_SCHEMA = {
    "itineraryId": "str UUID（主要索引）",
    "userId":      "str — 關聯 users.uid（索引）",
    "title":       "str",
    "days": [
        {
            "dayNumber": "int",
            "date":      "str YYYY-MM-DD | null",
            "spots": [
                {
                    "spotId":        "str UUID",
                    "placeId":       "str — Google Places ID",
                    "name":          "str",
                    "address":       "str — 完整地址（例如：2 Chome-3-1 Asakusa, Taito City, Tokyo, Japan）",
                    "location":      {"lat": "float", "lng": "float"},
                    "arrivalTime":   "str HH:MM",
                    "stayDuration":  "int 分鐘",
                    "rating":        "float | null",
                    "ticketPrice":   "float（新台幣）| null",
                    "bookingUrl":    "str | null",
                    "notes":         "str | null",
                }
            ]
        }
    ],
    "budget": {
        "total":     "float",
        "currency":  "str",
        "breakdown": "dict（各類費用）"
    },
    "createdAt": "datetime (UTC)",
    "updatedAt": "datetime (UTC)",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Collection: trips
# 使用者自建旅程（對應前端 travelStore 資料結構）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TRIP_STORE_SCHEMA = {
    "tripId":      "str UUID（主要索引）",
    "userId":      "str — 關聯 users.uid（索引）",
    "title":       "str",
    "destination": "str",
    "date":        "str YYYY/MM（顯示用月份）",
    "startDate":   "str YYYY-MM-DD",
    "endDate":     "str YYYY-MM-DD",
    "dates":       "str（顯示用區間文字）",
    "users":       "str（同行者）",
    "transfers":   "int（轉機次數）",
    "layovers":    "list — 轉機停靠點資訊",
    "fatigue":     "str — 疲勞指數顯示值",
    "weather":     "str — 天氣顯示值",
    "budget":      "str — 預算幣別",
    "currencyRate": "str",
    "currencyUpdatedAt": "str",
    "isUpcoming":  "bool",
    "coverImage":  "str URL",
    "note":        "str",
    "type":        "str",
    "flights": [
        {
            "flightNumber": "str",
            "airline":      "str",
            "departure": {
                "city": "str", "country": "str",
                "timezone": "str", "time": "str HH:MM"
            },
            "arrival": {
                "city": "str", "country": "str",
                "timezone": "str", "time": "str HH:MM"
            },
            "flightDurationHours": "float",
            "terminal": "str | null",
            "gate":     "str | null",
        }
    ],
    "itinerary": {
        "Day N": {
            "date":    "str YYYY-MM-DD",
            "weather": "str emoji",
            "items": [
                {
                    "id":          "str UUID",
                    "time":        "str HH:MM",
                    "title":       "str",
                    "location":    "str — 景點地點名稱",
                    "address":     "str — 完整地址（例如：2 Chome-3-1 Asakusa, Taito City, Tokyo, Japan）",
                    "category":    "str — transport|attraction|food|shopping|accommodation|city_walk",
                    "tags":        "list[str]",
                    "stayTime":    "float（小時）",
                    "cost":        "float（TWD）",
                    "description": "str",
                    "notes":       "str",
                    "image":       "str URL",
                }
            ]
        }
    },
    "packingItems": {
        "Day N": {
            "date":  "str YYYY-MM-DD",
            "items": [{"name": "str", "category": "str"}]
        }
    },
    "shoppingItems": [{"name": "str", "checked": "bool"}],
    "createdAt": "datetime (UTC)",
    "updatedAt": "datetime (UTC)",
}
