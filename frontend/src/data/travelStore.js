import { reactive, watch } from 'vue'
import travelData from './travelData.json'

const STORAGE_KEY = 'travelwise:data'

export const cloneData = (value) => JSON.parse(JSON.stringify(value))

const formatDateForDisplay = (date) => date.replace(/-/g, '/')

const parseDateParts = (date) => date.split('-').map(Number)

const toDateUtc = (date) => {
  const [year, month, day] = parseDateParts(date)
  return new Date(Date.UTC(year, month - 1, day))
}

const formatDateUtc = (date) => {
  const year = date.getUTCFullYear()
  const month = String(date.getUTCMonth() + 1).padStart(2, '0')
  const day = String(date.getUTCDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

const getTripDayCount = (startDate, endDate) => {
  const start = toDateUtc(startDate)
  const end = toDateUtc(endDate)
  return Math.ceil(Math.abs(end - start) / (1000 * 60 * 60 * 24)) + 1
}

const addDays = (date, days) => {
  const result = toDateUtc(date)
  result.setUTCDate(result.getUTCDate() + days)
  return formatDateUtc(result)
}

const getDayOffset = (startDate, endDate) => {
  const start = toDateUtc(startDate)
  const end = toDateUtc(endDate)
  return Math.max(0, Math.round((end - start) / (1000 * 60 * 60 * 24)))
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

const isReturnFlight = (flight, firstFlight) => {
  if (!flight || !firstFlight) return false

  return (
    flight.departure?.city === firstFlight.arrival?.city &&
    flight.arrival?.city === firstFlight.departure?.city
  )
}

const getFlightDateRange = (flights = [], fallbackStartDate = '', fallbackEndDate = '') => {
  const firstFlight = flights[0]
  const lastFlight = flights[flights.length - 1]
  const startDate = firstFlight?.departure?.date || fallbackStartDate
  const explicitReturnDate = lastFlight?.returnDate ||
    (isReturnFlight(lastFlight, firstFlight) ? lastFlight?.departure?.date || lastFlight?.arrival?.date : '')
  const fallbackDuration = fallbackStartDate && fallbackEndDate ? getDayOffset(fallbackStartDate, fallbackEndDate) : 0
  const endDate = explicitReturnDate || (startDate ? addDays(startDate, fallbackDuration) : fallbackEndDate)

  return { startDate, endDate }
}

const normalizeFlight = (flight, tripStartDate, tripEndDate, index, flights) => {
  const firstFlight = flights[0]
  const isLastFlight = index === flights.length - 1
  const shouldUseReturnDate = isLastFlight && (flight.returnDate || isReturnFlight(flight, firstFlight))
  const departureDate = flight.departure?.date || (shouldUseReturnDate ? tripEndDate : tripStartDate)
  const arrivalDate = flight.arrival?.date || departureDate

  return {
    ...flight,
    departure: {
      ...(flight.departure || {}),
      date: departureDate
    },
    arrival: {
      ...(flight.arrival || {}),
      date: arrivalDate
    }
  }
}

const buildTripDateFields = (startDate, endDate) => {
  const dayCount = getTripDayCount(startDate, endDate)

  return {
    startDate,
    endDate,
    date: startDate.substring(0, 7).replace('-', '/'),
    dates: `${formatDateForDisplay(startDate)}-${formatDateForDisplay(endDate)}, 共${dayCount}天`
  }
}

const normalizeTravelData = (data) => {
  const normalizedData = cloneData(data)

  normalizedData.trips = (normalizedData.trips || []).map((trip) => {
    const initialFlights = Array.isArray(trip.flights) ? trip.flights : []
    const range = getFlightDateRange(initialFlights, trip.startDate, trip.endDate)
    const dateFields = buildTripDateFields(range.startDate, range.endDate)
    const flights = initialFlights.map((flight, index) =>
      normalizeFlight(flight, dateFields.startDate, dateFields.endDate, index, initialFlights)
    )

    return {
      ...trip,
      ...dateFields,
      transfers: Number(trip.transfers || 0),
      layovers: Array.isArray(trip.layovers) ? trip.layovers : [],
      flights,
      itinerary: syncDayMapToDates(
        Object.fromEntries(
      Object.entries(trip.itinerary || {}).map(([dayName, dayData]) => [
        dayName,
        {
          ...dayData,
          items: (dayData.items || []).map(normalizeItineraryItem)
        }
      ])
        ),
        dateFields.startDate,
        dateFields.endDate,
        (date) => ({ date, weather: '-', items: [] })
      ),
      packingItems: syncDayMapToDates(
        trip.packingItems,
        dateFields.startDate,
        dateFields.endDate,
        (date) => ({ date, items: [] })
      )
    }
  })

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
  const range = getFlightDateRange(formData.flights, formData.startDate, formData.endDate)
  const dateFields = buildTripDateFields(range.startDate, range.endDate)
  const companionText = formData.companion.trim() ? formData.companion : '僅自己'
  const flights = (formData.flights || []).map((flight, index, allFlights) =>
    normalizeFlight(flight, dateFields.startDate, dateFields.endDate, index, allFlights)
  )

  return {
    id: `trip-${Date.now()}`,
    date: dateFields.date,
    title: formData.destination,
    destination: formData.destination,
    users: companionText,
    startDate: dateFields.startDate,
    endDate: dateFields.endDate,
    dates: dateFields.dates,
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
    flights,
    itinerary: createDayMap(dateFields.startDate, dateFields.endDate, (date) => ({
      date,
      weather: '-',
      items: []
    })),
    packingItems: createDayMap(dateFields.startDate, dateFields.endDate, (date) => ({
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

  const sourceFlights = formData.flights || target.flights || []
  const range = getFlightDateRange(sourceFlights, formData.startDate, formData.endDate)
  const dateFields = buildTripDateFields(range.startDate, range.endDate)
  const companionText = formData.companion.trim() ? formData.companion : '僅自己'
  const flights = sourceFlights.map((flight, index, allFlights) =>
    normalizeFlight(flight, dateFields.startDate, dateFields.endDate, index, allFlights)
  )

  Object.assign(target, {
    date: dateFields.date,
    title: formData.destination,
    destination: formData.destination,
    users: companionText,
    startDate: dateFields.startDate,
    endDate: dateFields.endDate,
    dates: dateFields.dates,
    transfers: Number(formData.transfers || 0),
    layovers: cloneData(formData.layovers || []),
    fatigue: Number(formData.transfers || 0) > 0 ? '計算中...' : target.fatigue,
    flights
  })

  target.itinerary = syncDayMapToDates(
    target.itinerary,
    dateFields.startDate,
    dateFields.endDate,
    (date) => ({ date, weather: '-', items: [] })
  )
  target.packingItems = syncDayMapToDates(
    target.packingItems,
    dateFields.startDate,
    dateFields.endDate,
    (date) => ({ date, items: [] })
  )

  persistTravelData()
  return target
}

export const resetTravelData = () => {
  trips.splice(0, trips.length, ...normalizeTravelData(travelData).trips)
  persistTravelData()
}
