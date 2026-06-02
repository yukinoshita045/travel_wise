import client from './client'

/** 查詢目的地天氣與衣物建議（Open-Meteo，免費不需 Key）
 *  @param {string} destination  城市名稱（英文），如 "Tokyo"
 *  @returns axios Response，data 結構：
 *   { destination, forecast: [{date, condition, tempMax, tempMin, ...}], clothingSuggestion, alerts }
 */
export const fetchWeather = (destination) =>
  client.get('/api/weather', { params: { destination } })
