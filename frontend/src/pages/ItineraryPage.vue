<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { v4 as uuidv4 } from 'uuid'
import AddItineraryModal from '../components/itinerary/AddItineraryModal.vue'
import DetailItineraryModal from '../components/itinerary/DetailItineraryModal.vue'
import EditItineraryModal from '../components/itinerary/EditItineraryModal.vue'
import Navbar from '../components/Navbar.vue'
import WeatherIcon from '../components/WeatherIcon.vue'
import ChatPanel from '../components/chat/ChatPanel.vue'
import { getTripOrDefault, saveTripChanges } from '../data/travelStore.js'

const route = useRoute()
const router = useRouter()
const trip = computed(() => getTripOrDefault(route.params.id))
const tripData = computed(() => trip.value.itinerary || {})
const getInitialSelectedDay = () => {
  const queryDay = route.query.day
  return typeof queryDay === 'string' && tripData.value[queryDay]
    ? queryDay
    : Object.keys(tripData.value)[0] || 'Day 1'
}

const selectedDay = ref(getInitialSelectedDay())
const openMenu = ref(null)
const showModal = ref(false)
const showEditModal = ref(false)
const selectedItinerary = ref(null)
const chatLayout = ref({ isOpen: false, width: 0 })

const packingItems = ref([])

watch(
  () => route.query.day,
  (day) => {
    if (typeof day === 'string' && tripData.value[day]) {
      selectedDay.value = day
    }
  }
)

const handleAddPrepItem = (prepItem) => {
  const exists = packingItems.value.some(
    (item) =>
      item.name === prepItem.name &&
      item.date === prepItem.date &&
      item.itineraryId === prepItem.itineraryId
  )

  if (exists) return

  packingItems.value.push(prepItem)

  console.log('packingItems', packingItems.value)
}

const form = ref({
  id:'',
  time: '',
  title: '',
  location: '',
  address:'',
  stayTime: 0,
  description: '',
  image: '',
})

const editForm = ref({
  id: '',
  time: '',
  title: '',
  location: '',
  address: '',
  stayTime: '',
  description: '',
  image: '',
})

const openEditModal = (item) => {
  editForm.value = {
    id: item.id,
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
  const items = tripData.value[selectedDay.value].items

  const index = items.findIndex(i => i.id === updated.id)

  if (index !== -1) {
    items[index] = {
      ...items[index],
      ...updated,
    }
    saveTripChanges(trip.value.id || trip.value.tripId)
  }

  showEditModal.value = false
}

const handleAdd = () => {
  showModal.value = true
}

const handleSubmit = (payload) => {
  console.log('payload', payload)

  const newItem = {
    ...payload,
    time: payload.time || '00:00',
    stayTime: Number(payload.stayTime || 0),
    id: uuidv4(),
  }

  tripData.value[selectedDay.value].items.push(newItem)
  saveTripChanges(trip.value.id || trip.value.tripId)

  form.value = {
    id: '',
    time: '',
    title: '',
    location: '',
    address: '',
    stayTime: 0,
    description: '',
    image: '',
  }

  showModal.value = false
}
const handleDelete = (day, idToDelete) => {
  tripData.value[day].items = tripData.value[day].items.filter(
    (i) => i.id !== idToDelete
  )
  saveTripChanges(trip.value.id || trip.value.tripId)
  openMenu.value = null
}

const goBack = () => {
  router.push(`/trip/${trip.value.id}`)
}

const handleChatLayoutChange = (layout) => {
  chatLayout.value = layout
}
</script>

<template>
  <div
    class="h-screen overflow-hidden bg-[#F8FAFC] px-6 pb-6 pt-24 flex flex-col transition-[padding-left] duration-200"
    :style="{ paddingLeft: chatLayout.isOpen ? `${chatLayout.width + 24}px` : undefined }"
  >
    <Navbar />

    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold text-[#1E293B]">
        行程規劃
      </h1>

      <button
        @click="goBack"
        class="rounded-full bg-[#94A3B8] px-4 py-2 text-white"
      >
        ← 返回
      </button>
    </div>

    <!-- Day Switch -->
    <div class="mb-6 flex gap-3 overflow-x-auto">
      <button
        v-for="(data, day) in tripData"
        :key="day"
        @click="selectedDay = day"
        class="flex items-center gap-2 rounded-full px-5 py-2 whitespace-nowrap"
        :class="selectedDay === day ? 'bg-[#94A3B8] text-white' : 'bg-white text-gray-700 shadow-sm'"
      >
        <span>{{ day }}</span>
        <WeatherIcon
          v-if="data.weather"
          :weather="data.weather"
          size-class="h-4 w-4"
        />
      </button>
    </div>

    <!-- Card -->
    <div class="flex-1 overflow-hidden rounded-3xl bg-white p-8 shadow-xl flex flex-col">

      <div class="mb-6 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-[#1E293B]">
            {{ selectedDay }}
            <WeatherIcon
              v-if="tripData[selectedDay].weather"
              :weather="tripData[selectedDay].weather"
              size-class="ml-2 inline h-6 w-6"
            />
          </h2>
          <p class="text-sm text-gray-500">
            {{ tripData[selectedDay].date }}
          </p>
        </div>

        <button
          @click="handleAdd"
          class="h-10 w-10 rounded-full bg-[#94A3B8] text-white"
        >
          +
        </button>
      </div>

      <div class="relative flex-1 overflow-y-auto pr-2 space-y-8">

        <div
          v-for="(item, index) in [...tripData[selectedDay].items].sort((a, b) => (a.time || '').localeCompare(b.time || ''))"
          :key="item.id"
          class="flex gap-6"
        >

          <div class="flex flex-col items-center">
            <p class="text-sm text-[#64748B]">{{ item.time }}</p>
            <div class="my-2 h-4 w-4 rounded-full bg-[#94A3B8]" />
            <div
              v-if="index !== tripData[selectedDay].items.length - 1"
              class="w-[2px] flex-1 bg-[#CBD5E1]"
            />
          </div>

          <div class="relative flex flex-1 flex-col cursor-pointer"
               @click="selectedItinerary = item">

            <div class="h-[180px] rounded-3xl bg-[#F8FAFC] p-4 shadow-sm">

              <div class="flex h-full gap-4">

                <div class="aspect-square h-full shrink-0 overflow-hidden rounded-2xl bg-slate-200">
                  <img
                    v-if="item.image"
                    :src="item.image"
                    class="h-full w-full object-cover"
                  />
                </div>

                <div class="flex flex-1 flex-col">

                  <div class="flex justify-between">

                    <div>
                      <h3 class="font-semibold text-[#1E293B]">
                        {{ item.title }}
                      </h3>
                      <p class="text-sm text-gray-500">
                        {{ item.location }}
                      </p>
                    </div>

                    <div class="relative" @click.stop>
                      <button
                        @click="openMenu = openMenu === item.id ? null : item.id"
                      >
                        ⋯
                      </button>

                      <div
                        v-if="openMenu === item.id"
                        class="absolute right-0 top-8 w-28 rounded-xl bg-white shadow border"
                      >
                        <button
                          @click="handleDelete(selectedDay, item.id)"
                          class="w-full px-3 py-2 text-left text-red-500 hover:bg-gray-100"
                        >
                          刪除
                        </button>
                      </div>
                    </div>

                  </div>

                  <p class="mt-3 text-sm text-gray-600">
                    {{ item.description }}
                  </p>

                  <div class="mt-auto flex justify-end text-sm text-[#64748B]">
                    停留 {{ item.stayTime }} 小時
                  </div>

                </div>

              </div>

            </div>
          </div>

        </div>

      </div>
    </div>

    <AddItineraryModal
      v-model:form="form"
      :show="showModal"
      @close="showModal = false"
      @submit="handleSubmit"
    />
<!-- 
    <DetailItineraryModal
      :item="selectedItinerary"
      @close="selectedItinerary = null"
      @edit="openEditModal"
    /> -->

    <DetailItineraryModal
      :item="selectedItinerary"
      :date="tripData[selectedDay].date"
      @close="selectedItinerary = null"
      @edit="openEditModal"
      @add-prep-item="handleAddPrepItem"
    />

    <EditItineraryModal
      :show="showEditModal"
      :model-value="editForm"
      @close="showEditModal = false"
      @submit="handleUpdate"
    />

    <ChatPanel
      :trip-id="String(route.params.id)"
      @layout-change="handleChatLayoutChange"
    />

  </div>
</template>
