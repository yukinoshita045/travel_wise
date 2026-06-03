import { reactive, watch } from 'vue'
import travelData from './travelData.json'
import {
  fetchTrips,
  createTrip as apiCreateTrip,
  updateTripApi,
  deleteTripApi,
  syncTrips as apiSyncTrips,
} from '../api/trips'
import { fetchWeather } from '../api/weather'
import { fetchRates, inferCurrencyFromDestination } from '../api/currency'
import { analyzeFatigue } from '../api/fatigue'

const STORAGE_KEY = 'travelwise:data'

export const cloneData = (value) => JSON.parse(JSON.stringify(value))

const normalizeItineraryItem = (item) => {
  const normalizedItem = {
    ...item,
    title: item.title || item.name || '未命名行程',
    address: item.address || '',
  }

  delete normalizedItem.name
  delete normalizedItem.stay
  delete normalizedItem.lat
  delete normalizedItem.lng
  delete normalizedItem.lon
  delete normalizedItem.move

  return normalizedItem
}

const normalizeTravelData = (data) => {
  const normalizedData = cloneData(data)

  normalizedData.trips = (normalizedData.trips || []).map((trip) => ({
    ...trip,
    transfers: Number(trip.transfers || 0),
    layovers: Array.isArray(trip.layovers) ? trip.layovers : [],
    itinerary: Object.fromEntries(
      Object.entries(trip.itinerary || {}).map(([dayName, dayData]) => [
        dayName,
        {
          ...dayData,
          items: (dayData.items || []).map(normalizeItineraryItem),
        },
      ])
    ),
  }))

  return normalizedData
}

const getInitialTravelData = () => {
  if (typeof window === 'undefined') return normalizeTravelData(travelData)

  try {
    const savedData = window.localStorage.getItem(STORAGE_KEY)
    if (!savedData) return normalizeTravelData(travelData)

    const parsedData = JSON.parse(savedData)
    return Array.isArray(parsedData?.trips)
      ? normalizeTravelData(parsedData)
      : normalizeTravelData(travelData)
  } catch (error) {
    console.warn('讀取暫存旅程資料失敗，改用 travelData.json。', error)
    return normalizeTravelData(travelData)
  }
}

export const travelStore = reactive({
  trips: getInitialTravelData().trips,
  /** true 代表正在與後端同步 */
  syncing: false,
  /** 後端是否可用 */
  apiOnline: false,
})

export const trips = travelStore.trips

export const getTripById = (id) =>
  trips.find((trip) => String(trip.id || trip.tripId) === String(id))

export const getDefaultTrip = () => trips[0]

export const getTripOrDefault = (id) => getTripById(id) || getDefaultTrip()

// ── localStorage 持久化 ──────────────────────────────────────
const persistTravelData = () => {
  if (typeof window === 'undefined') return
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cloneData({ trips: travelStore.trips })))
  } catch (error) {
    console.warn('儲存暫存旅程資料失敗。', error)
  }
}

persistTravelData()

watch(
  () => travelStore.trips,
  () => { persistTravelData() },
  { deep: true }
)

// ── 後端同步：把 MongoDB 回傳的 trip 欄位對應回前端格式 ────────
const normalizeApiTrip = (apiTrip) => {
  // MongoDB 用 tripId，前端用 id
  const normalized = normalizeTravelData({ trips: [{ ...apiTrip, id: apiTrip.tripId || apiTrip.id }] })
  return normalized.trips[0]
}

// ── 啟動時嘗試從後端載入旅程 ────────────────────────────────
export const loadTripsFromApi = async () => {
  try {
    travelStore.syncing = true
    const res = await fetchTrips()
    const apiTrips = res.data?.trips || []

    if (apiTrips.length > 0) {
      // 以後端資料為主，完全替換本地資料
      trips.splice(0, trips.length, ...apiTrips.map(normalizeApiTrip))
      persistTravelData()
      travelStore.apiOnline = true
      console.info(`[TravelStore] 從後端載入 ${apiTrips.length} 筆旅程 ✅`)
    } else {
      // 後端沒有資料時，把本地資料同步上去
      travelStore.apiOnline = true
      if (trips.length > 0) {
        await apiSyncTrips(cloneData(trips))
        console.info(`[TravelStore] 將本地 ${trips.length} 筆旅程同步到後端 ✅`)
      }
    }
  } catch (err) {
    console.warn('[TravelStore] 無法連線到後端，使用本地快取。', err?.message || err)
    travelStore.apiOnline = false
  } finally {
    travelStore.syncing = false
  }
}

// ── 日期工具函式 ────────────────────────────────────────────
const formatDateForDisplay = (date) => date.replace(/-/g, '/')

const getTripDayCount = (startDate, endDate) => {
  const start = new Date(`${startDate}T00:00:00`)
  const end = new Date(`${endDate}T00:00:00`)
  return Math.ceil(Math.abs(end - start) / (1000 * 60 * 60 * 24)) + 1
}

const addDays = (date, days) => {
  const result = new Date(`${date}T00:00:00`)
  result.setDate(result.getDate() + days)
  return result.toISOString().slice(0, 10)
}

const createDayMap = (startDate, endDate, createDayData) => {
  const dayCount = getTripDayCount(startDate, endDate)
  return Array.from({ length: dayCount }).reduce((result, _, index) => {
    const dayName = `Day ${index + 1}`
    result[dayName] = createDayData(addDays(startDate, index), dayName, index)
    return result
  }, {})
}

const syncDayMapToDates = (dayMap, startDate, endDate, createEmptyDayData) => {
  const nextDayMap = createDayMap(startDate, endDate, (date, dayName) => ({
    ...createEmptyDayData(date),
    ...(dayMap?.[dayName] || {}),
    date,
  }))
  return nextDayMap
}

export const createTripFromForm = (formData) => {
  const dayCount = getTripDayCount(formData.startDate, formData.endDate)
  const displayDates = `${formatDateForDisplay(formData.startDate)}-${formatDateForDisplay(formData.endDate)}, 共${dayCount}天`
  const displayMonth = formData.startDate.substring(0, 7).replace('-', '/')
  const companionText = formData.companion.trim() ? formData.companion : '僅自己'

  return {
    id: `trip-${Date.now()}`,
    date: displayMonth,
    title: formData.destination,
    destination: formData.destination,
    users: companionText,
    startDate: formData.startDate,
    endDate: formData.endDate,
    dates: displayDates,
    type: '行程規劃',
    transfers: Number(formData.transfers || 0),
    layovers: cloneData(formData.layovers || []),
    fatigue: Number(formData.transfers || 0) > 0 ? '計算中...' : '預估低',
    weather: '-',
    budget: 'TWD',
    currencyRate: '-',
    currencyUpdatedAt: '',
    isUpcoming: true,
    coverImage: 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1400',
    note: '行程筆記：',
    flights: [],
    itinerary: createDayMap(formData.startDate, formData.endDate, (date) => ({
      date,
      weather: '-',
      items: [],
    })),
    packingItems: createDayMap(formData.startDate, formData.endDate, (date) => ({
      date,
      items: [],
    })),
    shoppingItems: [],
  }
}

// ── addTrip：本地先加，再非同步推到後端 ─────────────────────
export const addTrip = async (formData) => {
  const trip = createTripFromForm(formData)
  trips.unshift(trip)
  persistTravelData()

  if (travelStore.apiOnline) {
    try {
      const res = await apiCreateTrip(cloneData(trip))
      const saved = res.data?.trip
      if (saved) {
        // 以後端回傳的 tripId 更新本地 id（保持一致）
        const local = getTripById(trip.id)
        if (local && saved.tripId) local.id = saved.tripId
        persistTravelData()
      }
    } catch (err) {
      console.warn('[TravelStore] addTrip 後端同步失敗，保留本地版本。', err?.message)
    }
  }

  return trip
}

// ── updateTrip：本地先更新，再非同步推到後端 ─────────────────
export const updateTrip = async (tripId, formData) => {
  const target = getTripById(tripId)
  if (!target) return null

  const dayCount = getTripDayCount(formData.startDate, formData.endDate)
  const displayDates = `${formatDateForDisplay(formData.startDate)}-${formatDateForDisplay(formData.endDate)}, 共${dayCount}天`
  const displayMonth = formData.startDate.substring(0, 7).replace('-', '/')
  const companionText = formData.companion.trim() ? formData.companion : '僅自己'

  Object.assign(target, {
    date: displayMonth,
    title: formData.destination,
    destination: formData.destination,
    users: companionText,
    startDate: formData.startDate,
    endDate: formData.endDate,
    dates: displayDates,
    transfers: Number(formData.transfers || 0),
    layovers: cloneData(formData.layovers || []),
    fatigue: Number(formData.transfers || 0) > 0 ? '計算中...' : target.fatigue,
  })

  target.itinerary = syncDayMapToDates(
    target.itinerary,
    formData.startDate,
    formData.endDate,
    (date) => ({ date, weather: '-', items: [] })
  )
  target.packingItems = syncDayMapToDates(
    target.packingItems,
    formData.startDate,
    formData.endDate,
    (date) => ({ date, items: [] })
  )

  persistTravelData()

  if (travelStore.apiOnline) {
    try {
      await updateTripApi(tripId, cloneData(target))
    } catch (err) {
      console.warn('[TravelStore] updateTrip 後端同步失敗，保留本地版本。', err?.message)
    }
  }

  return target
}

// ── deleteTrip：本地刪除 + 後端刪除 ─────────────────────────
export const deleteTrip = async (tripId) => {
  const idx = trips.findIndex((t) => String(t.id || t.tripId) === String(tripId))
  if (idx === -1) return false
  trips.splice(idx, 1)
  persistTravelData()

  if (travelStore.apiOnline) {
    try {
      await deleteTripApi(tripId)
    } catch (err) {
      console.warn('[TravelStore] deleteTrip 後端同步失敗。', err?.message)
    }
  }

  return true
}

// ── 儲存單筆旅程的變更（行程 items 編輯後呼叫）───────────────
export const saveTripChanges = async (tripId) => {
  if (!travelStore.apiOnline) return
  const trip = getTripById(tripId)
  if (!trip) return
  try {
    await updateTripApi(tripId, cloneData(trip))
  } catch (err) {
    console.warn('[TravelStore] saveTripChanges 後端同步失敗。', err?.message)
  }
}

export const resetTravelData = () => {
  trips.splice(0, trips.length, ...normalizeTravelData(travelData).trips)
  persistTravelData()
}

// ── 航班：新增 / 移除單筆航班，並重新計算疲勞 ─────────────────
export const addFlightToTrip = async (tripId, flightData) => {
  const trip = getTripById(tripId)
  if (!trip || !flightData) return
  if (!Array.isArray(trip.flights)) trip.flights = []
  trip.flights.push(flightData)
  persistTravelData()
  await saveTripChanges(tripId)
  // 航班變動會影響轉機次數與時差，重新計算疲勞
  refreshFatigueForTrip(tripId)
  return trip.flights
}

export const removeFlightFromTrip = async (tripId, index) => {
  const trip = getTripById(tripId)
  if (!trip || !Array.isArray(trip.flights)) return
  trip.flights.splice(index, 1)
  persistTravelData()
  await saveTripChanges(tripId)
  refreshFatigueForTrip(tripId)
  return trip.flights
}

// ── 匯率：查詢並更新旅程的 currencyRate / currencyUpdatedAt ──
export const refreshCurrencyForTrip = async (tripId) => {
  const trip = getTripById(tripId)
  if (!trip) return

  const toCurrency = inferCurrencyFromDestination(trip.destination)
  if (!toCurrency) return // 無法推斷幣別，跳過

  try {
    const res = await fetchRates('TWD')
    const rates = res.data?.rates || {}
    const rate = rates[toCurrency]
    if (!rate) return

    const now = new Date()
    const timeStr = now.toLocaleTimeString('zh-TW', { hour: '2-digit', minute: '2-digit' })
    trip.currencyRate = `1 TWD = ${rate.toFixed(2)} ${toCurrency}`
    trip.currencyUpdatedAt = `最後更新：${timeStr}`
    trip.budget = 'TWD'
    persistTravelData()
    console.info(`[TravelStore] 匯率已更新 → ${trip.currencyRate}`)
  } catch (err) {
    console.warn('[TravelStore] 匯率查詢失敗。', err?.message)
  }
}

// ── 天氣：查詢並寫入每天的 weather emoji ──────────────────────
const conditionToEmoji = (condition = '') => {
  if (condition.includes('snow') || condition.includes('雪')) return '❄'
  if (condition.includes('rain') || condition.includes('drizzle') || condition.includes('雨')) return '☔'
  if (condition.includes('wind') || condition.includes('風')) return '🌬'
  if (condition.includes('cloud') || condition.includes('overcast') || condition.includes('陰')) return '🌥'
  if (condition.includes('clear') || condition.includes('sunny') || condition.includes('晴')) return '☀'
  return '🌤'
}

// 中文目的地 → 英文城市名（給 Open-Meteo / OpenTripMap geocoding 使用）
export const toEnglishDestination = (destination = '') => {
  const map = {
    '東京': 'Tokyo', '大阪': 'Osaka', '京都': 'Kyoto', '札幌': 'Sapporo',
    '福岡': 'Fukuoka', '名古屋': 'Nagoya', '沖繩': 'Okinawa', '日本': 'Japan',
    '首爾': 'Seoul', '釜山': 'Busan', '濟州': 'Jeju', '韓國': 'Korea',
    '曼谷': 'Bangkok', '清邁': 'Chiang Mai', '普吉': 'Phuket', '泰國': 'Thailand',
    '香港': 'Hong Kong', '新加坡': 'Singapore',
    '北京': 'Beijing', '上海': 'Shanghai', '廣州': 'Guangzhou', '深圳': 'Shenzhen',
    '倫敦': 'London', '巴黎': 'Paris', '紐約': 'New York', '洛杉磯': 'Los Angeles',
    '河內': 'Hanoi', '胡志明': 'Ho Chi Minh City', '吉隆坡': 'Kuala Lumpur',
    '雪梨': 'Sydney', '墨爾本': 'Melbourne',
  }
  for (const [zh, en] of Object.entries(map)) {
    if (destination.includes(zh)) return en
  }
  return destination // 本來就是英文或未知，直接傳
}

export const refreshWeatherForTrip = async (tripId) => {
  const trip = getTripById(tripId)
  if (!trip || !trip.destination) return

  try {
    const englishDest = toEnglishDestination(trip.destination)
    const res = await fetchWeather(englishDest)
    const forecast = res.data?.forecast || []
    if (!forecast.length) return

    // 建立 date → condition 的 map
    const dateMap = {}
    forecast.forEach((f) => { dateMap[f.date] = f.condition })

    // 把每天的天氣 emoji 寫進 itinerary
    Object.values(trip.itinerary || {}).forEach((day) => {
      if (day.date && dateMap[day.date]) {
        day.weather = conditionToEmoji(dateMap[day.date])
      }
    })

    persistTravelData()
    console.info(`[TravelStore] 天氣已更新 (${trip.destination})`)
  } catch (err) {
    console.warn('[TravelStore] 天氣查詢失敗。', err?.message)
  }
}

// ── 疲勞指數：從第一段航班計算並寫回 trip.fatigue ─────────────
export const refreshFatigueForTrip = async (tripId) => {
  const trip = getTripById(tripId)
  if (!trip) return

  const flight = trip.flights?.[0]
  if (!flight) return // 沒有航班資料，跳過

  const dep = flight.departure
  const arr = flight.arrival
  if (!dep?.timezone || !arr?.timezone || !flight.flightDurationHours) return

  try {
    const payload = {
      departureTimezone:   dep.timezone,
      arrivalTimezone:     arr.timezone,
      flightDurationHours: flight.flightDurationHours,
      layoverCount:        (trip.flights?.length || 1) - 1,
      isRedEye:            false,
      travelers:           [{ ageGroup: 'adult', fitnessLevel: 'medium' }],
      hasNapped:           false,
    }
    const res = await analyzeFatigue(payload)
    const data = res.data
    if (data?.baseScore == null) return

    trip.fatigue = `${data.baseScore}%`
    trip._fatigueDetail = data // 保存完整 detail 供 FlightPage 使用
    persistTravelData()
    console.info(`[TravelStore] 疲勞指數已更新 → ${trip.fatigue}`)
  } catch (err) {
    console.warn('[TravelStore] 疲勞分析失敗。', err?.message)
  }
}

// ── 一次更新單筆旅程的所有即時資料（匯率 + 天氣 + 疲勞）──────
export const refreshTripLiveData = (tripId) => {
  refreshCurrencyForTrip(tripId)
  refreshWeatherForTrip(tripId)
  refreshFatigueForTrip(tripId)
}
