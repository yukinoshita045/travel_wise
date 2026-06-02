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

/** 根據目的地字串推斷目標幣別（支援中英文）
 *  e.g. "Tokyo, Japan" / "日本東京" → "JPY"
 */
export const inferCurrencyFromDestination = (destination = '') => {
  const d = destination.toLowerCase()

  // 日本
  if (d.includes('japan') || d.includes('tokyo') || d.includes('osaka') ||
      d.includes('kyoto') || d.includes('日本') || d.includes('東京') ||
      d.includes('大阪') || d.includes('京都') || d.includes('札幌') ||
      d.includes('福岡') || d.includes('名古屋') || d.includes('沖繩'))
    return 'JPY'

  // 韓國
  if (d.includes('korea') || d.includes('seoul') || d.includes('busan') ||
      d.includes('jeju') || d.includes('韓國') || d.includes('首爾') ||
      d.includes('釜山') || d.includes('濟州'))
    return 'KRW'

  // 泰國
  if (d.includes('thailand') || d.includes('bangkok') || d.includes('chiang') ||
      d.includes('phuket') || d.includes('泰國') || d.includes('曼谷') ||
      d.includes('清邁') || d.includes('普吉'))
    return 'THB'

  // 香港
  if (d.includes('hong kong') || d.includes('hongkong') ||
      d.includes('香港'))
    return 'HKD'

  // 新加坡
  if (d.includes('singapore') || d.includes('新加坡'))
    return 'SGD'

  // 中國
  if (d.includes('china') || d.includes('beijing') || d.includes('shanghai') ||
      d.includes('中國') || d.includes('北京') || d.includes('上海') ||
      d.includes('廣州') || d.includes('深圳'))
    return 'CNY'

  // 澳洲
  if (d.includes('australia') || d.includes('sydney') || d.includes('melbourne') ||
      d.includes('澳洲') || d.includes('雪梨') || d.includes('墨爾本'))
    return 'AUD'

  // 英國
  if (d.includes('uk') || d.includes('london') || d.includes('england') ||
      d.includes('英國') || d.includes('倫敦'))
    return 'GBP'

  // 歐洲
  if (d.includes('europe') || d.includes('france') || d.includes('germany') ||
      d.includes('italy') || d.includes('spain') || d.includes('paris') ||
      d.includes('歐洲') || d.includes('法國') || d.includes('德國') ||
      d.includes('義大利') || d.includes('西班牙') || d.includes('巴黎'))
    return 'EUR'

  // 美國
  if (d.includes('usa') || d.includes('new york') || d.includes('los angeles') ||
      d.includes('america') || d.includes('美國') || d.includes('紐約') ||
      d.includes('洛杉磯') || d.includes('舊金山'))
    return 'USD'

  // 越南
  if (d.includes('vietnam') || d.includes('hanoi') || d.includes('ho chi minh') ||
      d.includes('越南') || d.includes('河內') || d.includes('胡志明'))
    return 'VND'

  // 馬來西亞
  if (d.includes('malaysia') || d.includes('kuala lumpur') ||
      d.includes('馬來西亞') || d.includes('吉隆坡'))
    return 'MYR'

  return null // 無法推斷
}
