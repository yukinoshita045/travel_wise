/**
 * api/trip.js
 * AI 相關端點封裝：
 *   - /api/chat            聊天式行程建議（ChatPanel 使用）
 *   - /api/trip/plan       一站式行程規劃（航班+疲勞+AI 行程）
 *   - /api/itinerary/*     AI 生成行程文件 CRUD（存 MongoDB）
 */
import client from './client'

// ── 聊天 ──────────────────────────────────────────────
export const sendChat = (payload) => client.post('/api/chat', payload)

// ── 一站式行程規劃 ────────────────────────────────────
/** @param payload { flight, travelers, trip, fatigueScore? } 詳見後端 /api/trip/plan */
export const planTrip = (payload) => client.post('/api/trip/plan', payload)

// ── AI 行程文件（itinerary）CRUD ──────────────────────
/** AI 生成行程並存入 MongoDB */
export const recommendItinerary = (params) =>
  client.post('/api/itinerary/recommend', params)

/** 取得使用者所有歷史行程 */
export const getItineraryHistory = () =>
  client.get('/api/itinerary/user/history')

/** 取得單一 AI 行程文件 */
export const getItinerary = (id) => client.get(`/api/itinerary/${id}`)

/** 更新 AI 行程文件 */
export const updateItinerary = (id, data) =>
  client.put(`/api/itinerary/${id}`, data)

/** 刪除 AI 行程文件 */
export const deleteItinerary = (id) => client.delete(`/api/itinerary/${id}`)
