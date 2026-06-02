/**
 * api/trips.js
 * 旅程 CRUD API — 對應後端 /api/trips
 */
import client from './client'

/** 取得所有旅程 */
export const fetchTrips = () => client.get('/api/trips')

/** 建立新旅程 */
export const createTrip = (tripData) => client.post('/api/trips', tripData)

/** 取得單一旅程 */
export const fetchTrip = (tripId) => client.get(`/api/trips/${tripId}`)

/** 更新旅程（含行程 items、address 等） */
export const updateTripApi = (tripId, tripData) =>
  client.put(`/api/trips/${tripId}`, tripData)

/** 刪除旅程 */
export const deleteTripApi = (tripId) => client.delete(`/api/trips/${tripId}`)

/**
 * 批次同步（把 localStorage 所有旅程一次推送到後端）
 * payload: { trips: [...] }
 */
export const syncTrips = (trips) => client.post('/api/trips/sync', { trips })
