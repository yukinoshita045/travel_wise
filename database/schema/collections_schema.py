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
                    "address":       "str",
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
