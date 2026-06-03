/**
 * api/flight.js
 * 航班即時資訊查詢 — 對應後端 GET /api/flight/info
 * 回傳資料結構與 trip.flights[] 完全一致，可直接寫入旅程。
 */
import client from './client'

/** 查詢單一航班即時起降 / 航廈 / 時區資料
 *  @param {string} flightNum 航班編號，如 "IT203"
 *  @param {string} date      出發日期，格式 YYYY-MM-DD
 *  @returns axios Response，data: {
 *    flightNumber, airline,
 *    departure: { code, city, country, timezone, terminal, gate, time },
 *    arrival:   { code, city, country, timezone, terminal, gate, time },
 *    flightDurationHours
 *  }
 */
export const fetchFlightInfo = (flightNum, date) =>
  client.get('/api/flight/info', { params: { flightNum, date } })
