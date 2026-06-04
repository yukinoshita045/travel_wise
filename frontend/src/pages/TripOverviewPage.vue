<template>
  <div class="min-h-screen bg-[#f4f7fb] px-[8vw] pb-10 pt-24 font-sans text-[#263245] max-[900px]:px-4 max-[900px]:pb-[30px]">
    <Navbar />

    <div class="mb-4 flex justify-end">
      <button
        @click="router.push('/')"
        class="rounded-full bg-[#94A3B8] px-4 py-2 text-sm font-medium text-white shadow transition hover:opacity-90"
      >
        ← 返回
      </button>
    </div>

    <div
      class="h-[190px] rounded-b-[24px] bg-cover bg-center max-[900px]:h-[150px]"
      :style="{ backgroundImage: `linear-gradient(to bottom, rgba(255,255,255,0), rgba(255,255,255,.15)), url(${trip.coverImage})` }"
    ></div>

    <section class="mt-3 grid grid-cols-2 gap-[14px] max-[900px]:grid-cols-1">
      <div
        @click="openTripEditModal"
        class="flex h-[70px] cursor-pointer items-center rounded-[22px] border-[1.5px] border-[#94a9c5] bg-white px-[22px] shadow-[0_8px_20px_rgba(49,74,107,.06)] transition hover:-translate-y-0.5 hover:shadow-[0_12px_24px_rgba(49,74,107,.10)]"
        title="編輯行程"
      >
        <span class="mr-4 text-[26px]">📍</span>
        <div class="min-w-0">
          <h1 class="text-2xl font-bold">{{ trip.destination }}</h1>
          <p class="mt-1 text-[15px] text-slate-500">{{ trip.dates.replace(', ', '・') }}</p>
        </div>
      </div>

      <div class="relative h-[70px] rounded-[22px] border-[1.5px] border-[#94a9c5] bg-white px-[22px] pt-2.5 shadow-[0_8px_20px_rgba(49,74,107,.06)]">
        <p class="text-[13px] text-[#7b8ba1]">{{ trip.note }}</p>
        <div class="mt-2.5 h-px bg-[#9aabc2]"></div>
        <div class="mt-2.5 h-px w-[82%] bg-[#9aabc2]"></div>
        <button
          type="button"
          @click="handleNoteClick"
          class="absolute right-[18px] top-5 bg-transparent text-2xl text-[#8da0bb]"
        >
          ✎
        </button>
      </div>
    </section>

    <section class="mt-[14px] grid grid-cols-4 gap-[14px] max-[900px]:grid-cols-1">
      <div
        v-for="card in summaryCards"
        :key="card.title"
        @click="handleSummaryCardClick(card)"
        class="relative h-[136px] rounded-[22px] bg-white p-4 shadow-[0_8px_20px_rgba(49,74,107,.06)]"
        :class="card.action || card.path ? 'cursor-pointer transition hover:-translate-y-0.5 hover:shadow-[0_12px_24px_rgba(49,74,107,.10)]' : ''"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5 text-[13px] text-[#7f8fa7]">
            <span class="h-[34px] w-[34px] rounded-full bg-[#70839d]"></span>
            {{ card.title }}
          </div>

          <strong v-if="card.count">{{ card.count }}</strong>
        </div>

        <template v-if="card.type === 'flight' && currentFlight">
          <div class="mt-2 flex min-w-0 items-center gap-1.5">
            <h3 class="shrink-0 text-[15px] font-bold leading-tight text-[#263245]">
              {{ currentFlight.flightNumber }}
            </h3>
            <span class="text-[11px] font-medium leading-tight text-[#94a3b8]">·</span>
            <p class="truncate text-[11px] font-medium leading-tight text-[#7f8fa7]">
              {{ currentFlight.airline }}
            </p>
          </div>

          <div class="mt-2 flex items-center justify-between gap-2">
            <button
              v-if="hasPreviousFlight"
              type="button"
              @click.stop="showPreviousFlight"
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#eef3f8] text-sm font-bold text-[#70839d] transition hover:bg-[#dce6f1]"
              aria-label="上一筆航班"
            >
              <ChevronLeft class="h-4 w-4 text-[#70839d]" :stroke-width="3" />
            </button>
            <span v-else class="h-6 w-6 shrink-0"></span>

            <div class="min-w-0 text-left">
              <p class="text-base font-black leading-none text-[#263245]">
                {{ formatAirportCode(currentFlight.departure) }}
              </p>
              <p class="mt-1 text-[10px] font-semibold leading-none text-[#7f8fa7]">
                {{ formatFlightTime(currentFlight.departure) }}
              </p>
            </div>
            <div class="shrink-0 text-center">
              <p class="text-sm font-bold leading-none text-[#94a3b8]">→</p>
              <p class="mt-1 whitespace-nowrap text-[10px] font-semibold leading-none text-[#7f8fa7]">
                {{ formatFlightDate(currentFlight) }}
              </p>
            </div>
            <div class="min-w-0 text-right">
              <p class="text-base font-black leading-none text-[#263245]">
                {{ formatAirportCode(currentFlight.arrival) }}
              </p>
              <p class="mt-1 text-[10px] font-semibold leading-none text-[#7f8fa7]">
                {{ formatFlightTime(currentFlight.arrival) }}
              </p>
            </div>

            <button
              v-if="hasNextFlight"
              type="button"
              @click.stop="showNextFlight"
              class="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#eef3f8] text-sm font-bold text-[#70839d] transition hover:bg-[#dce6f1]"
              aria-label="下一筆航班"
            >
              <ChevronRight class="h-4 w-4 text-[#70839d]" :stroke-width="3" />
            </button>
            <span v-else class="h-6 w-6 shrink-0"></span>
          </div>
        </template>

        <template v-else>
          <h3 v-if="card.heading" class="mt-[14px] text-lg font-bold">
            {{ card.heading }}
          </h3>

          <p
            v-for="text in card.texts"
            :key="text"
            class="mt-2 text-[13px] text-[#66768d]"
          >
            {{ text }}
          </p>
        </template>

        <button
          v-if="card.showPlus"
          @click.stop="handleSummaryPlusClick(card)"
          class="absolute bottom-3 right-4 flex h-9 w-9 items-center justify-center rounded-full bg-[#27c77a] text-2xl text-white transition hover:scale-110 hover:bg-[#1fb86d]"
        >
          ＋
        </button>
      </div>
    </section>

    <section
      class="mt-4 flex w-full gap-[14px] overflow-x-auto pb-2.5
      [&::-webkit-scrollbar]:h-2
      [&::-webkit-scrollbar-thumb]:rounded-full
      [&::-webkit-scrollbar-thumb]:bg-[#c4cfdd]"
    >
      <div
        v-for="day in days"
        :key="day.id"
        @click="openItineraryDay(day.title)"
        class="flex h-[500px] w-[calc((100%-42px)/4)] min-w-[280px] shrink-0 flex-col rounded-[22px] bg-white p-[18px] shadow-[0_8px_20px_rgba(49,74,107,.06)] max-[900px]:w-full"
        :class="'cursor-pointer transition hover:-translate-y-0.5 hover:shadow-[0_12px_24px_rgba(49,74,107,.10)]'"
      >
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-[22px] font-bold">{{ day.title }}</h2>
            <p class="mt-1 text-xs text-[#8ea0b8]">{{ day.date }}</p>
          </div>

          <WeatherIcon :weather="day.weather" size-class="h-8 w-8" />
        </div>

        <div
          class="mt-[14px] flex-1 overflow-y-auto pr-1
          [&::-webkit-scrollbar]:w-[5px]
          [&::-webkit-scrollbar-thumb]:rounded-full
          [&::-webkit-scrollbar-thumb]:bg-[#cbd5e2]"
        >
          <div
            v-for="(item, index) in getSortedDayItems(day)"
            :key="item.id || index"
            @click.stop="openItineraryDetail(item, day)"
            class="mb-5 grid grid-cols-[14px_minmax(0,1fr)] gap-2.5"
          >
            <div class="relative flex justify-center">
              <div
                v-if="index !== getSortedDayItems(day).length - 1"
                class="absolute top-[12px] bottom-[-20px] w-px bg-[#cbd5e2]"
              ></div>
              <div class="relative z-10 mt-[2px] h-3 w-3 rounded-full bg-[#70839d]"></div>
            </div>

            <div class="min-w-0">
              <p class="mb-1.5 truncate text-[13px] font-bold tabular-nums text-[#64748B]" :title="item.time">
                {{ item.time }}
              </p>

              <div class="flex min-h-[92px] items-center gap-3 rounded-[14px] bg-[#f6f8fb] p-[14px]">
                <div class="h-[72px] w-[72px] shrink-0 overflow-hidden rounded-lg bg-slate-200">
                  <img
                    v-if="item.image"
                    :src="item.image"
                    :alt="getItemTitle(item)"
                    class="h-full w-full object-cover"
                  />
                </div>

                <div class="min-w-0 flex-1">
                  <h3 class="truncate text-lg font-bold">{{ getItemTitle(item) }}</h3>
                  <p class="mt-1.5 line-clamp-2 text-xs text-[#8494aa]">
                    {{ getItemDescription(item) }}
                  </p>
                </div>
              </div>

              <div class="mt-2.5 text-xs text-[#8798af]">
                <span>{{ getStayText(item) }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <AddItemModal
      :show="showPackingModal"
      :day-options="packingDayOptions"
      :category-options="categoryOptions"
      @close="showPackingModal = false"
      @submit="addPackingItem"
    />

    <ShoppingListModal
      v-model="shoppingItems"
      :show="showShoppingModal"
      @close="showShoppingModal = false"
    />

    <DetailItineraryModal
      :item="selectedItinerary"
      :date="selectedItineraryDate"
      @close="selectedItinerary = null"
      @edit="openEditModal"
    />

    <EditItineraryModal
      :show="showEditModal"
      :model-value="editForm"
      :day-options="itineraryDayOptions"
      @close="showEditModal = false"
      @submit="handleUpdate"
    />

    <BudgetModal
      :show="showBudgetModal"
      :trip="trip"
      @close="showBudgetModal = false"
    />

    <CurrencyModal
      :show="showCurrencyModal"
      :trip="trip"
      @close="showCurrencyModal = false"
    />

    <TripModal
      v-if="showTripEditModal"
      :trip-data="trip"
      :is-submitting="isTripSubmitting"
      @close="closeTripEditModal"
      @submit="handleTripEditSubmit"
    />

  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, ChevronRight } from 'lucide-vue-next'
import Navbar from '../components/Navbar.vue'
import AddItemModal from '../components/item/AddItemModal.vue'
import ShoppingListModal from '../components/shopping/ShoppingListModal.vue'
import DetailItineraryModal from '../components/itinerary/DetailItineraryModal.vue'
import EditItineraryModal from '../components/itinerary/EditItineraryModal.vue'
import WeatherIcon from '../components/WeatherIcon.vue'
import BudgetModal from '../components/BudgetModal.vue'
import CurrencyModal from '../components/CurrencyModal.vue'
import TripModal from '../components/TripModal.vue'
import { getTripOrDefault, saveTripChanges, refreshTripLiveData, updateTrip } from '../data/travelStore.js'

const route = useRoute()
const router = useRouter()
const trip = computed(() => getTripOrDefault(route.params.id))

const showBudgetModal = ref(false)
const showCurrencyModal = ref(false)
const showTripEditModal = ref(false)
const isTripSubmitting = ref(false)

onMounted(() => {
  const id = route.params.id || trip.value?.id
  if (id) refreshTripLiveData(id)
})
const showShoppingModal = ref(false)
const showPackingModal = ref(false)
const selectedItinerary = ref(null)
const selectedItineraryDate = ref('')
const selectedItineraryDay = ref('')
const showEditModal = ref(false)
const editForm = ref({
  id: '',
  day: '',
  time: '',
  title: '',
  location: '',
  address: '',
  stayTime: '',
  description: '',
  image: '',
})

const allPackingItems = computed(() =>
  Object.values(trip.value.packingItems || {}).flatMap((day) => day.items || [])
)

const packingDayOptions = computed(() =>
  Object.entries(trip.value.packingItems || {}).map(([day, data]) => ({
    day,
    date: data.date,
  }))
)

const categoryOptions = computed(() => {
  const categories = []

  allPackingItems.value.forEach((item) => {
    if (item.category && !categories.includes(item.category)) {
      categories.push(item.category)
    }
  })

  return categories
})

const shoppingItems = computed({
  get: () => trip.value.shoppingItems || [],
  set: (items) => {
    trip.value.shoppingItems = items
  },
})

const firstFlight = computed(() => trip.value.flights?.[0])
const flightIndex = ref(0)
const flightCount = computed(() => trip.value.flights?.length || 0)
const currentFlight = computed(() => {
  if (!flightCount.value) return null

  const safeIndex = Math.min(flightIndex.value, flightCount.value - 1)
  return trip.value.flights?.[safeIndex]
})
const hasPreviousFlight = computed(() => flightIndex.value > 0)
const hasNextFlight = computed(() => flightIndex.value < flightCount.value - 1)

const padTime = (value) => String(value).padStart(2, '0')

const normalizeDateTime = (value) => {
  if (!value) return { date: '', time: '' }

  const text = String(value).trim()
  const dateMatch = text.match(/^(\d{4}-\d{2}-\d{2})/)
  const timeMatch = text.match(/(?:T|\s)(\d{2}):(\d{2})/) || text.match(/^(\d{1,2}):(\d{2})/)

  return {
    date: dateMatch?.[1] || '',
    time: timeMatch ? `${padTime(timeMatch[1])}:${timeMatch[2]}` : text
  }
}

const formatAirportCode = (segment) => segment?.code || segment?.city || '-'

const formatFlightTime = (segment) => normalizeDateTime(segment?.time).time || '-'

const formatFlightDate = (flight) => {
  const date = flight?.departure?.date || normalizeDateTime(flight?.departure?.time).date
  return date ? date.replace(/-/g, '/') : '-'
}

const showPreviousFlight = () => {
  if (hasPreviousFlight.value) flightIndex.value -= 1
}

const showNextFlight = () => {
  if (hasNextFlight.value) flightIndex.value += 1
}

const openTripEditModal = () => {
  showTripEditModal.value = true
}

const closeTripEditModal = () => {
  if (!isTripSubmitting.value) showTripEditModal.value = false
}

const handleTripEditSubmit = async (formData) => {
  isTripSubmitting.value = true

  try {
    await updateTrip(trip.value.id || trip.value.tripId, formData)
  } finally {
    isTripSubmitting.value = false
    closeTripEditModal()
  }
}

const handleNoteClick = () => {
  alert('行程筆記功能開發中，敬請期待！')
}

const summaryCards = computed(() => [
  {
    type: 'flight',
    title: '航班資訊',
    heading: currentFlight.value ? `${currentFlight.value.flightNumber} ${currentFlight.value.airline}` : '尚未新增航班',
    texts: currentFlight.value
      ? [`${formatFlightTime(currentFlight.value.departure)} → ${formatFlightTime(currentFlight.value.arrival)}`]
      : ['點此管理航班'],
    path: `/trip/${trip.value.id}/flights`
  },
  {
    title: '準備清單',
    count: allPackingItems.value.length,
    texts: allPackingItems.value.slice(0, 2).map((item) => `○ ${item.name}`),
    showPlus: true,
    plusAction: 'openPackingModal',
    path: `/trip/${trip.value.id}/items`
  },
  {
    title: '購物清單',
    count: trip.value.shoppingItems?.length || 0,
    texts: (trip.value.shoppingItems || []).slice(0, 2).map((item) => `○ ${item.name}`),
    showPlus: true,
    action: 'openShoppingModal',
    plusAction: 'openShoppingModal'
  },
  {
    title: '即時匯率',
    heading: trip.value.currencyRate,
    texts: [trip.value.currencyUpdatedAt || '點此換算金額'],
    action: 'openCurrencyModal'
  },
  // {
  //   title: '預算試算',
  //   heading: trip.value.budget ? `幣別 ${trip.value.budget}` : '預算分配',
  //   texts: ['點此估算住宿/餐費/交通'],
  //   action: 'openBudgetModal'
  // }
])

const handleSummaryCardClick = (card) => {
  if (card.action === 'openShoppingModal') {
    showShoppingModal.value = true
    return
  }

  if (card.action === 'openBudgetModal') {
    showBudgetModal.value = true
    return
  }

  if (card.action === 'openCurrencyModal') {
    showCurrencyModal.value = true
    return
  }

  if (card.path) router.push(card.path)
}

const handleSummaryPlusClick = (card) => {
  if (card.plusAction === 'openPackingModal') {
    showPackingModal.value = true
  }

  if (card.plusAction === 'openShoppingModal') {
    showShoppingModal.value = true
  }
}

const openItineraryDay = (dayTitle) => {
  router.push({
    path: `/trip/${trip.value.id}/itinerary`,
    query: { day: dayTitle }
  })
}

const openItineraryDetail = (item, day) => {
  selectedItinerary.value = item
  selectedItineraryDate.value = day.rawDate
  selectedItineraryDay.value = day.title
}

const openEditModal = (item) => {
  editForm.value = {
    id: item.id,
    day: selectedItineraryDay.value,
    time: item.time,
    title: item.title,
    location: item.location,
    address: item.address,
    stayTime: item.stayTime,
    description: item.description,
    image: item.image,
  }

  showEditModal.value = true
  selectedItinerary.value = null
}

const handleUpdate = (updated) => {
  const sourceDay = editForm.value.day || selectedItineraryDay.value
  const targetDay = updated.day || sourceDay
  const sourceItems = trip.value.itinerary?.[sourceDay]?.items || []
  const targetItems = trip.value.itinerary?.[targetDay]?.items || sourceItems
  const index = sourceItems.findIndex((item) => item.id === updated.id)

  if (index !== -1) {
    const updatedItem = {
      ...sourceItems[index],
      ...updated,
    }
    delete updatedItem.day

    if (targetDay === sourceDay) {
      sourceItems[index] = updatedItem
    } else {
      sourceItems.splice(index, 1)
      targetItems.push(updatedItem)
      selectedItineraryDay.value = targetDay
      selectedItineraryDate.value = trip.value.itinerary?.[targetDay]?.date || selectedItineraryDate.value
    }

    saveTripChanges(trip.value.id || trip.value.tripId)
  }

  showEditModal.value = false
}

const addPackingItem = (item) => {
  if (!trip.value.packingItems?.[item.day]) return

  trip.value.packingItems[item.day].items.push({
    name: item.name,
    category: item.category || '未分類',
  })

  saveTripChanges(trip.value.id || trip.value.tripId)
  showPackingModal.value = false
}

const formatDayDate = (date) => {
  const parsed = new Date(`${date}T00:00:00`)
  return parsed.toLocaleDateString('en-US', {
    month: '2-digit',
    day: '2-digit',
    weekday: 'short'
  }).replace(',', '')
}

const getItemTitle = (item) => item.title || '未命名行程'

const getItemDescription = (item) => item.description || item.location || '尚未填寫描述'

const getStayText = (item) => {
  if (item.stayTime || item.stayTime === 0) return `停留 ${item.stayTime} 小時`
  return '尚未設定停留時間'
}

const getSortedDayItems = (day) =>
  [...(day.items || [])].sort((a, b) => (a.time || '').localeCompare(b.time || ''))

const days = computed(() =>
  Object.entries(trip.value.itinerary || {}).map(([title, day], index) => ({
    id: `${trip.value.id}-${index}`,
    title,
    rawDate: day.date,
    date: formatDayDate(day.date),
    weather: day.weather,
    items: day.items
  }))
)

const itineraryDayOptions = computed(() =>
  days.value.map((day) => ({
    value: day.title,
    label: `${day.title} ・ ${day.rawDate}`,
  }))
)
</script>
