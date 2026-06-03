/**
 * api/places.js
 * 景點搜尋 / 詳情 — 對應後端 /api/places（OpenTripMap）
 */
import client from './client'

/** 搜尋城市景點
 *  @param {object} opts {
 *    city: string,          // 城市名（建議英文，如 "Tokyo"）
 *    preferences?: string[],// 偏好：文化/自然/美食/拍照/購物/宗教/娛樂/歷史
 *    radius?: number,       // 搜尋半徑（公尺），預設 5000
 *    limit?: number         // 筆數，預設 20
 *  }
 *  @returns axios Response，data: [{ xid, name, lat, lon, kinds, rate, dist }]
 */
export const searchPlaces = ({ city, preferences = [], radius = 5000, limit = 20 }) =>
  client.get('/api/places/search', {
    params: {
      city,
      preferences: preferences.join(','),
      radius,
      limit,
    },
  })

/** 取得單一景點詳情（OpenTripMap xid） */
export const getPlaceDetail = (xid) => client.get(`/api/places/${xid}`)
