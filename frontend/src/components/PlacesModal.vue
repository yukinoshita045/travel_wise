<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div class="flex max-h-[90vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
      <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
        <h3 class="flex items-center gap-2 text-xl font-bold text-slate-800">
          <span class="inline-block h-6 w-2 rounded-full bg-[#94A3B8]"></span>
          景點搜尋
        </h3>
        <button @click="$emit('close')" class="p-1 text-slate-400 hover:text-slate-700">✕</button>
      </div>

      <div class="space-y-4 border-b border-slate-100 p-6">
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-600">城市（建議英文）</label>
          <input
            v-model="city"
            type="text"
            placeholder="例如：Tokyo"
            class="w-full rounded-lg border border-slate-300 px-4 py-2 outline-none focus:border-[#94A3B8] focus:ring-2 focus:ring-[#94A3B8]/40"
            @keyup.enter="runSearch"
          />
        </div>
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-600">偏好類型</label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="p in allPrefs"
              :key="p"
              @click="togglePref(p)"
              class="rounded-full border px-3 py-1 text-sm transition"
              :class="selectedPrefs.includes(p)
                ? 'border-[#94A3B8] bg-[#94A3B8] text-white'
                : 'border-slate-300 text-slate-600 hover:bg-slate-50'"
            >
              {{ p }}
            </button>
          </div>
        </div>
        <button
          @click="runSearch"
          :disabled="loading"
          class="w-full rounded-lg bg-[#94A3B8] py-2 font-bold text-white shadow transition hover:opacity-90 disabled:opacity-60"
        >
          {{ loading ? '搜尋中...' : '搜尋景點' }}
        </button>
        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>
      </div>

      <!-- 結果列表 -->
      <div class="flex-1 overflow-y-auto p-6">
        <p v-if="!loading && searched && results.length === 0" class="text-center text-sm text-slate-400">
          找不到符合的景點，試試其他城市或偏好
        </p>
        <ul class="space-y-2">
          <li
            v-for="spot in results"
            :key="spot.xid"
            class="flex items-center justify-between rounded-xl border border-slate-100 px-4 py-3"
          >
            <div class="min-w-0">
              <p class="truncate font-medium text-slate-800">{{ spot.name }}</p>
              <p class="truncate text-xs text-slate-400">{{ spot.kinds }}</p>
            </div>
            <button
              @click="$emit('add', spot)"
              class="ml-3 shrink-0 rounded-full bg-[#27c77a] px-3 py-1 text-sm font-medium text-white transition hover:bg-[#1fb86d]"
            >
              ＋ 加入
            </button>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { searchPlaces } from '../api/places.js'
import { toEnglishDestination } from '../data/travelStore.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  trip: { type: Object, required: true },
})
defineEmits(['close', 'add'])

const allPrefs = ['文化', '自然', '美食', '拍照', '購物', '宗教', '娛樂', '歷史']
const city = ref('')
const selectedPrefs = ref(['文化', '歷史'])
const results = ref([])
const loading = ref(false)
const error = ref('')
const searched = ref(false)

watch(
  () => props.show,
  (open) => {
    if (open) {
      city.value = toEnglishDestination(props.trip?.destination || '')
      results.value = []
      error.value = ''
      searched.value = false
    }
  }
)

const togglePref = (p) => {
  const i = selectedPrefs.value.indexOf(p)
  if (i === -1) selectedPrefs.value.push(p)
  else selectedPrefs.value.splice(i, 1)
}

const runSearch = async () => {
  error.value = ''
  if (!city.value.trim()) {
    error.value = '請輸入城市名稱'
    return
  }
  loading.value = true
  searched.value = true
  try {
    const res = await searchPlaces({
      city: city.value.trim(),
      preferences: selectedPrefs.value,
      radius: 5000,
      limit: 20,
    })
    results.value = Array.isArray(res.data) ? res.data : []
  } catch (err) {
    error.value = err?.response?.data?.error || '搜尋失敗，請確認城市名稱（建議英文）'
    results.value = []
  } finally {
    loading.value = false
  }
}
</script>
