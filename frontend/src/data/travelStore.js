import { reactive, watch } from 'vue'
import travelData from './travelData.json'

const STORAGE_KEY = 'travelwise:data'

export const cloneData = (value) => JSON.parse(JSON.stringify(value))

const normalizeItineraryItem = (item) => {
  const normalizedItem = {
    ...item,
    title: item.title || item.name || '未命名行程'
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
    itinerary: Object.fromEntries(
      Object.entries(trip.itinerary || {}).map(([dayName, dayData]) => [
        dayName,
        {
          ...dayData,
          items: (dayData.items || []).map(normalizeItineraryItem)
        }
      ])
    )
  }))

  return normalizedData
}

const getInitialTravelData = () => {
  if (typeof window === 'undefined') return normalizeTravelData(travelData)

  try {
    const savedData = window.localStorage.getItem(STORAGE_KEY)
    if (!savedData) return normalizeTravelData(travelData)

    const parsedData = JSON.parse(savedData)
    return Array.isArray(parsedData?.trips) ? normalizeTravelData(parsedData) : normalizeTravelData(travelData)
  } catch (error) {
    console.warn('讀取暫存旅程資料失敗，改用 travelData.json。', error)
    return normalizeTravelData(travelData)
  }
}

export const travelStore = reactive({
  trips: getInitialTravelData().trips
})

export const trips = travelStore.trips

export const getTripById = (id) => trips.find((trip) => String(trip.id) === String(id))

export const getDefaultTrip = () => trips[0]

export const getTripOrDefault = (id) => getTripById(id) || getDefaultTrip()

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
    date
  }))

  return nextDayMap
}

const persistTravelData = () => {
  if (typeof window === 'undefined') return

  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(cloneData(travelStore)))
  } catch (error) {
    console.warn('儲存暫存旅程資料失敗。', error)
  }
}

persistTravelData()

watch(
  travelStore,
  () => {
    persistTravelData()
  },
  { deep: true }
)

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
    fatigue: formData.needLayover ? '計算中...' : '預估低',
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
      items: []
    })),
    packingItems: createDayMap(formData.startDate, formData.endDate, (date) => ({
      date,
      items: []
    })),
    shoppingItems: []
  }
}

export const addTrip = (formData) => {
  const trip = createTripFromForm(formData)
  trips.unshift(trip)
  persistTravelData()
  return trip
}

export const updateTrip = (tripId, formData) => {
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
    fatigue: formData.needLayover ? '計算中...' : target.fatigue
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
  return target
}

export const resetTravelData = () => {
  trips.splice(0, trips.length, ...normalizeTravelData(travelData).trips)
  persistTravelData()
}
