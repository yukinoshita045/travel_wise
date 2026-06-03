/**
 * api/budget.js
 * 預算分配試算 — 對應後端 POST /api/budget/calculate
 */
import client from './client'

/** 計算預算分配
 *  @param {object} payload {
 *    totalBudget: number,
 *    days: number,
 *    travelers: number,
 *    spots: [{ name, ticketPrice }],
 *    currency?: string  // 預設 "TWD"
 *  }
 *  @returns axios Response，data: {
 *    totalBudget, currency, perPerson, days, travelers,
 *    breakdown: { accommodation, food, transport, activities, emergency },
 *    warnings: string[], isOverBudget: boolean
 *  }
 */
export const calculateBudget = (payload) =>
  client.post('/api/budget/calculate', payload)
