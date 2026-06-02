import client from './client'

/** 飛行疲勞分析（SAFTE 模型）
 *  @param {object} payload
 *   { departureTimezone, arrivalTimezone, flightDurationHours,
 *     layoverCount, isRedEye, travelers, hasNapped }
 *  @returns axios Response，data: { baseScore, level, energyBattery,
 *    jetLagIndex, suggestedStartTime, tripStressType, recoverHours, explanation }
 */
export const analyzeFatigue = (payload) =>
  client.post('/api/fatigue/analyze', payload)
