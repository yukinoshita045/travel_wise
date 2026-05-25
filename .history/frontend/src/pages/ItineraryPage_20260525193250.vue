<script setup>
import { ref } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import AddItineraryModal from '../components/itiner/AddItineraryModal.vue'
import DetailItineraryModal from '../components/DetailItineraryModal.vue'
import EditItineraryModal from '../components/EditItineraryModal.vue'

const selectedDay = ref('Day 1')
const openMenu = ref(null)
const showModal = ref(false)
const showEditModal = ref(false)
const selectedItinerary = ref(null)

const tripData = ref({
  "Day 1": {
    date: "2026-01-01",
    items: [
      {
        id: uuidv4(),
        time: "09:00",
        title: "抵達桃園機場",
        location: "TPE Airport",
        address: "No. 9, Hangzhan S Rd, Dayuan District, Taoyuan City, Taiwan",
        lat: 25.0797,
        lng: 121.2342,
        category: "transport",
        tags: ["airport", "departure"],
        stayTime: 2,
        cost: 0,
        description: "提前 2 小時抵達機場，完成報到、托運與安檢流程。",
        notes: "記得確認護照與登機證",
        image:
          "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?q=80&w=1200&auto=format&fit=crop",
      },
      {
        id: uuidv4(),
        time: "11:30",
        title: "入住飯店",
        location: "Shinjuku Hotel",
        address: "2 Chome-14-5 Kabukicho, Shinjuku City, Tokyo, Japan",
        lat: 35.6938,
        lng: 139.7034,
        category: "accommodation",
        tags: ["hotel", "check-in"],
        stayTime: 1.5,
        cost: 4500,
        description: "辦理 Check-in，稍作休息後開始下午行程。",
        notes: "可提早寄放行李",
        image:
          "https://images.unsplash.com/photo-1566073771259-6a8506099945?q=80&w=1200&auto=format&fit=crop",
      },
      {
        id: uuidv4(),
        time: "14:00",
        title: "淺草寺",
        location: "Tokyo",
        address: "2 Chome-3-1 Asakusa, Taito City, Tokyo, Japan",
        lat: 35.7148,
        lng: 139.7967,
        category: "attraction",
        tags: ["temple", "culture"],
        stayTime: 3,
        cost: 0,
        description: "參觀雷門與仲見世商店街，體驗東京傳統文化。",
        notes: "建議避開人潮 15:00-17:00",
        image:
          "https://images.unsplash.com/photo-1526481280695-3c4691f8f6ac?q=80&w=1200&auto=format&fit=crop",
      },
    ],
  },

  "Day 2": {
    date: "2026-01-02",
    items: [
      {
        id: uuidv4(),
        time: "10:00",
        title: "東京迪士尼",
        location: "Tokyo Disney Resort",
        address: "1-1 Maihama, Urayasu, Chiba, Japan",
        lat: 35.6329,
        lng: 139.8804,
        category: "theme_park",
        tags: ["disney", "fun", "full-day"],
        stayTime: 8,
        cost: 8500,
        description: "全天樂園行程，建議提前預約熱門設施。",
        notes: "建議提早入園",
        image:
          "https://images.unsplash.com/photo-1582711012124-a56cf7a9bc6c?q=80&w=1200&auto=format&fit=crop",
      },
    ],
  },
})


const packingItems = ref([])

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
  openMenu.value = null
}
</script>

<template>
  <div class="h-screen overflow-hidden bg-[#F8FAFC] px-6 py-6 flex flex-col">

    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold text-[#1E293B]">
        行程規劃
      </h1>

      <button
        @click="window.history.back()"
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
        class="rounded-full px-5 py-2 whitespace-nowrap"
        :class="selectedDay === day ? 'bg-[#94A3B8] text-white' : 'bg-white text-gray-700 shadow-sm'"
      >
        {{ day }}
      </button>
    </div>

    <!-- Card -->
    <div class="flex-1 overflow-hidden rounded-3xl bg-white p-8 shadow-xl flex flex-col">

      <div class="mb-6 flex items-center justify-between">
        <div>
          <h2 class="text-xl font-bold text-[#1E293B]">
            {{ selectedDay }}
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

                <img
                  :src="item.image"
                  class="aspect-square h-full rounded-2xl object-cover"
                />

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

  </div>
</template>