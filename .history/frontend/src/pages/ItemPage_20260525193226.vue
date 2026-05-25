<script setup>
import { ref, computed } from 'vue'
import PackingButton from '../components/item/AddItemButton.vue'
import AddItemModal from '../components/item/AddItemModal.vue'
import ShoppingListModal from '../components/Shoppi1gListModal.vue'
import ShoppingButton from '../components/ShoppingButton.vue'

import {
  Luggage,
} from "lucide-vue-next";

const filter = ref('date')
const showModal = ref(false)

const editMode = ref(false)

const showDeleteConfirm = ref(false)

const deleteTarget = ref({
  day: '',
  index: null,
})

const itemData = ref({
  "Day 1": {
    date: "2026-01-01",
    items: [
      { name: "護照", category: "重要文件" },
      { name: "行動電源", category: "電子用品" },
      { name: "外套", category: "衣物" },
    ]
  },

  "Day 2": {
    date: "2026-01-02",
    items: [
      { name: "相機", category: "電子用品" },
      { name: "水壺", category: "生活用品" },
    ]
  },

  "Day 3": {
    date: "2026-01-03",
    items: [
      { name: "泳衣", category: "衣物" },
      { name: "防曬乳", category: "保養用品" },
    ]
  },

  "Day 4": {
    date: "2026-01-04",
    items: [
      { name: "野餐墊", category: "生活用品" }
    ]
  },

  "Day 5": {
    date: "2026-01-05",
    items: [
      { name: "拍立得", category: "電子用品" }
    ]
  }
})


const newItem = ref({
  name: '',
  day: '',
  category: '',
})

const showShoppingModal = ref(false)

const shoppingItems = ref([
  { name: '牙膏', checked: false },
  { name: '雨傘', checked: false },
  { name: '轉接頭', checked: false },
])

const dayOptions = computed(() => {
  return Object.entries(itemData.value).map(([day, data]) => ({
    day,
    date: data.date,
  }))
})

const categoryOptions = computed(() => {
  const categories = []

  Object.values(itemData.value).forEach((dayData) => {
    dayData.items.forEach((item) => {
      if (!categories.includes(item.category)) {
        categories.push(item.category)
      }
    })
  })

  return categories
})

const groupedByType = computed(() => {
  const result = {}

  Object.entries(itemData.value).forEach(([day, dayData]) => {
    dayData.items.forEach((item, index) => {
      if (!result[item.category]) {
        result[item.category] = []
      }

      result[item.category].push({
        ...item,
        day,
        date: dayData.date,
        originalIndex: index,
      })
    })
  })

  return result
})


const allItems = computed(() => {
  const result = []

  Object.entries(itemData.value).forEach(([day, dayData]) => {
    dayData.items.forEach((item, index) => {
      result.push({
        ...item,
        day,
        date: dayData.date,
        originalIndex: index,
      })
    })
  })

  return result
})

const addItem = (item) => {
  itemData.value[item.day].items.push({
    name: item.name,
    category: item.category || '未分類',
  })

  showModal.value = false
}

const closeModal = () => {
  newItem.value = {
    name: '',
    day: '',
    category: '',
  }

  showModal.value = false
}

const handleDeleteClick = (day, index) => {
  deleteTarget.value = {
    day,
    index,
  }

  showDeleteConfirm.value = true
}

const confirmDelete = () => {
  const { day, index } = deleteTarget.value

  itemData.value[day].items.splice(index, 1)

  showDeleteConfirm.value = false
}

const cancelDelete = () => {
  showDeleteConfirm.value = false
}

const goBack = () => {
  window.history.back()
}
</script>

<template>
  <div class="h-screen bg-[#F8FAFC] px-6 py-6 flex flex-col">
    
    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold text-[#1E293B]">
        準備清單
      </h1>

      <button
        @click="goBack"
        class="rounded-full bg-[#94A3B8] px-4 py-2 text-sm font-medium text-white shadow transition hover:opacity-90"
      >
        ← 返回
      </button>
    </div>

    <!-- Filter + Add -->
    <div class="mb-5 flex items-center justify-between gap-4">
      
      <!-- Filters -->
      <div class="flex gap-3 overflow-x-auto">
        <button
          v-for="type in ['date', 'type', 'all']"
          :key="type"
          @click="filter = type"
          :class="[
            'rounded-full px-5 py-2 text-sm font-medium transition whitespace-nowrap',
            filter === type
              ? 'bg-[#94A3B8] text-white'
              : 'bg-white text-gray-700 shadow-sm'
          ]"
        >
          {{
            type === 'date'
              ? '按日期'
              : type === 'type'
              ? '按類型'
              : '全部'
          }}
        </button>
      </div>

        <!-- Right Buttons -->
        <div class="flex items-center gap-3">

        <!-- Edit -->
        <button
            @click="editMode = !editMode"
            :class="[
            'rounded-full px-5 py-2 text-sm font-medium shadow transition whitespace-nowrap',
            editMode
                ? 'bg-red-400 text-white'
                : 'bg-white text-gray-700'
            ]"
        >
            {{ editMode ? '完成編輯' : '編輯' }}
        </button>

        <!-- Add -->
         <PackingButton @click="showModal = true" />
        <!-- <button
            @click="showModal = true"
            class="rounded-full bg-white px-5 py-2 text-sm font-medium text-gray-700 shadow transition hover:opacity-90 whitespace-nowrap"
        >
        <button
            @click="showModal = true"
            class="rounded-full bg-[#94A3B8] px-5 py-2 text-sm font-medium text-white shadow transition hover:opacity-90 whitespace-nowrap"
        >
            ＋ 新增物品
            <div class='flex flex-0 justify-between items-center gap-2'> 
                <Luggage class="h-4 w-4" />
                新增物品
            </div>
        </button> -->
        
        <!-- <button
          @click="showShoppingModal = true"
          class="rounded-full bg-white px-5 py-2 text-sm font-medium text-gray-700 shadow transition hover:opacity-90 whitespace-nowrap"
        >
          購物清單
        </button> -->
        <ShoppingButton @click="showShoppingModal = true" />
      </div>
        

    </div>

    <!-- Main Card -->
    <div class="flex-1 overflow-hidden rounded-3xl bg-white shadow-xl">
      
      <!-- DATE MODE -->
      <div
        v-if="filter === 'date'"
        class="flex h-full overflow-x-auto"
      >
        <div
          v-for="(dayData, day, index) in itemData"
          :key="day"
          class="relative w-[85vw] max-w-[320px] flex-shrink-0 flex flex-col h-full px-4 py-4"
        >
          
          <!-- divider -->
          <div
            v-if="index !== 0"
            class="absolute left-0 top-0 bottom-0 w-px bg-gray-200"
          />

          <!-- Title -->
          <div class="mb-4 flex justify-center">
            <h2 class="text-lg font-semibold text-gray-800">
              {{ day }}
            </h2>
          </div>

          <div class="flex justify-center">
            <p class="mt-1 text-sm text-gray-400">
              {{ dayData.date }}
            </p>
          </div>

          <!-- Items -->
          <div class="flex-1 overflow-y-auto space-y-3 pr-2">
            <div
              v-for="(item, idx) in dayData.items"
              :key="idx"
              class="flex items-center justify-between rounded-2xl border border-gray-100 bg-gray-50 px-4 py-4 transition hover:bg-gray-100"
            >
              <div>
                <p class="font-medium text-gray-800">
                  {{ item.name }}
                </p>

                <p class="mt-1 text-sm text-gray-500">
                  {{ item.category }}
                </p>
              </div>

              <!-- <input type="checkbox" class="h-5 w-5" /> -->

               <!-- normal mode -->
                <input
                v-if="!editMode"
                type="checkbox"
                class="h-5 w-5"
                />

                <!-- edit mode -->
                <button
                v-else
                @click="handleDeleteClick(day, idx)"
                class="flex h-6 w-6 items-center justify-center rounded-full bg-red-400 text-white"
                >
                −
                </button>
            </div>
          </div>

        </div>
      </div>

      <!-- TYPE MODE -->
      <div
        v-else-if="filter === 'type'"
        class="flex h-full overflow-x-auto"
      >
        <div
          v-for="(items, category, index) in groupedByType"
          :key="category"
          class="relative w-[85vw] max-w-[320px] flex-shrink-0 flex flex-col h-full px-4 py-4"
        >

          <!-- divider -->
          <div
            v-if="index !== 0"
            class="absolute left-0 top-0 bottom-0 w-px bg-gray-200"
          />

          <!-- Title -->
          <div class="mb-4 flex justify-center">
            <h2 class="text-lg font-semibold text-gray-800">
              {{ category }}
            </h2>
          </div>

          <!-- Items -->
          <div class="flex-1 overflow-y-auto space-y-3 pr-2">
            <div
              v-for="(item, idx) in items"
              :key="idx"
              class="flex items-center justify-between rounded-2xl border border-gray-100 bg-gray-50 px-4 py-4 transition hover:bg-gray-100"
            >
              <div>
                <p class="font-medium text-gray-800">
                  {{ item.name }}
                </p>

                <p class="mt-1 text-sm text-gray-500">
                  {{ item.day }} ・ {{ item.date }}
                </p>
              </div>

              <!-- <input type="checkbox" class="h-5 w-5" /> -->

               <input
                v-if="!editMode"
                type="checkbox"
                class="h-5 w-5"
                />

                <button
                v-else
                @click="handleDeleteClick(item.day, item.originalIndex)"
                class="flex h-6 w-6 items-center justify-center rounded-full bg-red-400 text-white"
                >
                −
                </button>
            </div>
          </div>

        </div>
      </div>

      <!-- ALL MODE -->
      <div
        v-else
        class="h-full overflow-y-auto p-5"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          
          <div
            v-for="(item, index) in allItems"
            :key="index"
            class="flex items-center justify-between rounded-2xl border border-gray-100 bg-gray-50 px-4 py-4 transition hover:bg-gray-100"
          >
            <div>
              <p class="font-medium text-gray-800">
                {{ item.name }}
              </p>

              <p class="mt-1 text-sm text-gray-500">
                {{ item.category }} ・ {{ item.day }} ・ {{ item.date }}
              </p>
            </div>

            <!-- <input type="checkbox" class="h-5 w-5" /> -->

             <input
            v-if="!editMode"
            type="checkbox"
            class="h-5 w-5"
            />

            <button
            v-else
            @click="handleDeleteClick(item.day, item.originalIndex)"
            class="flex h-6 w-6 items-center justify-center rounded-full bg-red-400 text-white"
            >
            −
            </button>
          </div>

        </div>
      </div>

    </div>

    <!-- ================= MODAL ================= -->
    <AddItemModal
      :show="showModal"
      :day-options="dayOptions"
      :category-options="categoryOptions"
      @close="showModal = false"
      @submit="addItem"
    />
    <ShoppingListModal
      v-model="shoppingItems"
      :show="showShoppingModal"
      @close="showShoppingModal = false"
    />
  </div>



  <!-- ================= DELETE CONFIRM ================= -->
  <div
    v-if="showDeleteConfirm"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
  >
    <div class="w-[360px] rounded-3xl bg-white p-6 shadow-xl">

      <h2 class="text-lg font-bold text-[#1E293B]">
        刪除物品
      </h2>

      <p class="mt-3 text-sm text-gray-500 leading-relaxed">
        你確定要刪除這個物品嗎？
      </p>

      <div class="mt-6 flex gap-3">

        <button
          @click="cancelDelete"
          class="flex-1 rounded-xl bg-gray-200 py-3 text-gray-700"
        >
          取消
        </button>

        <button
          @click="confirmDelete"
          class="flex-1 rounded-xl bg-red-400 py-3 text-white"
        >
          刪除
        </button>

      </div>

    </div>
  </div>
</template>