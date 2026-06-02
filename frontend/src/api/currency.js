import client from './client'

/** 取得以指定幣別為基準的所有匯率（ExchangeRate-API，Redis 快取 1hr）
 *  @param {string} base  基準幣別，預設 "TWD"
 *  @returns axios Response，data: { base, rates: {JPY: 4.67, ...}, supportedCurrencies }
 */
export const fetchRates = (base = 'TWD') =>
  client.get('/api/currency/rates', { params: { base } })

/** 金額換算
 *  @param {number} amount  要換算的金額
 *  @param {string} from    來源幣別，如 "TWD"
 *  @param {string} to      目標幣別，如 "JPY"
 *  @returns axios Response，data: { from, to, amount, converted, rate, fromName, toName }
 */
export const convertCurrency = (amount, from, to) =>
  client.post('/api/currency/convert', { amount, from, to })

/** 根據目的地字串推斷目標幣別
 *  e.g. "Tokyo, Japan" → "JPY"
 */
export const inferCurrencyFromDestination = (destination = '') => {
  const d = destination.toLowerCase()
  if (d.includes('japan') || d.includes('tokyo') || d.includes('osaka') || d.includes('kyoto')) return 'JPY'
  if (d.includes('korea') || d.includes('seoul') || d.includes('busan')) return 'KRW'
  if (d.includes('thailand') || d.includes('bangkok') || d.includes('chiang')) return 'THB'
  if (d.includes('hong kong') || d.includes('hongkong')) return 'HKD'
  if (d.includes('singapore')) return 'SGD'
  if (d.includes('china') || d.includes('beijing') || d.includes('shanghai')) return 'CNY'
  if (d.includes('australia') || d.includes('sydney') || d.includes('melbourne')) return 'AUD'
  if (d.includes('uk') || d.includes('london') || d.includes('england')) return 'GBP'
  if (d.includes('europe') || d.includes('france') || d.includes('germany') || d.includes('italy') || d.includes('spain')) return 'EUR'
  if (d.includes('usa') || d.includes('new york') || d.includes('los angeles') || d.includes('america')) return 'USD'
  return null // 未知目的地
}
