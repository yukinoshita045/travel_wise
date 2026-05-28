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
      <div class="flex h-[70px] items-center rounded-[22px] border-[1.5px] border-[#94a9c5] bg-white px-[22px] shadow-[0_8px_20px_rgba(49,74,107,.06)]">
        <span class="mr-4 text-[26px]">📍</span>
        <div>
          <h1 class="text-2xl font-bold">{{ trip.destination }}</h1>
          <p class="mt-1 text-[15px] text-slate-500">{{ trip.dates.replace(', ', '・') }}</p>
        </div>
      </div>

      <div class="relative h-[70px] rounded-[22px] border-[1.5px] border-[#94a9c5] bg-white px-[22px] pt-2.5 shadow-[0_8px_20px_rgba(49,74,107,.06)]">
        <p class="text-[13px] text-[#7b8ba1]">{{ trip.note }}</p>
        <div class="mt-2.5 h-px bg-[#9aabc2]"></div>
        <div class="mt-2.5 h-px w-[82%] bg-[#9aabc2]"></div>
        <button class="absolute right-[18px] top-5 bg-transparent text-2xl text-[#8da0bb]">
          ✎
        </button>
      </div>
    </section>

    <section class="mt-[14px] grid grid-cols-4 gap-[14px] max-[900px]:grid-cols-1">
      <div
        v-for="card in summaryCards"
        :key="card.title"
        @click="handleSummaryCardClick(card)"
        class="relative h-[120px] rounded-[22px] bg-white p-4 shadow-[0_8px_20px_rgba(49,74,107,.06)]"
        :class="card.action || card.path ? 'cursor-pointer transition hover:-translate-y-0.5 hover:shadow-[0_12px_24px_rgba(49,74,107,.10)]' : ''"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5 text-[13px] text-[#7f8fa7]">
            <span class="h-[34px] w-[34px] rounded-full bg-[#70839d]"></span>
            {{ card.title }}
          </div>

          <strong v-if="card.count">{{ card.count }}</strong>
        </div>

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

          <span class="text-[28px]">{{ day.weather }}</span>
        </div>

        <div
          class="mt-[14px] flex-1 overflow-y-auto pr-1
          [&::-webkit-scrollbar]:w-[5px]
          [&::-webkit-scrollbar-thumb]:rounded-full
          [&::-webkit-scrollbar-thumb]:bg-[#cbd5e2]"
        >
          <div
            v-for="(item, index) in day.items"
            :key="index"
            @click.stop="openItineraryDetail(item, day)"
            class="relative mb-5 border-l border-dashed border-[#a2b3c8] pl-5"
          >
            <div class="absolute left-[-5px] top-[6px] h-2 w-2 rounded-full bg-[#1f2d44]"></div>

            <div class="mb-2 text-[13px] font-bold">
              {{ item.time }}
            </div>

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

            <div class="mt-2.5 flex items-center justify-between gap-2 text-xs text-[#8798af]">
              <span>{{ getStayText(item) }}</span>
              <span v-if="item.move">🚆 {{ item.move }}</span>
            </div>
          </div>
        </div>
      </div>
    </section>

    <AddItemModal
      :show="showPackingModal"
      :day-options="dayOptions"
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
    />

  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import AddItemModal from '../components/item/AddItemModal.vue'
import ShoppingListModal from '../components/shopping/ShoppingListModal.vue'
import DetailItineraryModal from '../components/itinerary/DetailItineraryModal.vue'
import { getTripOrDefault } from '../data/travelStore.js'

const route = useRoute()
const router = useRouter()
const trip = computed(() => getTripOrDefault(route.params.id))
const showPackingModal = ref(false)
const showShoppingModal = ref(false)
const selectedItinerary = ref(null)
const selectedItineraryDate = ref('')

const allPackingItems = computed(() =>
  Object.values(trip.value.packingItems || {}).flatMap((day) => day.items || [])
)

const dayOptions = computed(() =>
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

const summaryCards = computed(() => [
  {
    title: '航班資訊',
    heading: firstFlight.value ? `${firstFlight.value.flightNumber} ${firstFlight.value.airline}` : '尚未新增航班',
    texts: firstFlight.value
      ? [`${firstFlight.value.departure.time} → ${firstFlight.value.arrival.time}`]
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
    texts: [trip.value.currencyUpdatedAt]
  }
])

const handleSummaryCardClick = (card) => {
  if (card.action === 'openShoppingModal') {
    showShoppingModal.value = true
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
}

const addPackingItem = (item) => {
  if (!trip.value.packingItems?.[item.day]) return

  trip.value.packingItems[item.day].items.push({
    name: item.name,
    category: item.category || '未分類',
  })

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
</script>
