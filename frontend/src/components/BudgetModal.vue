<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div class="flex max-h-[90vh] w-full max-w-lg flex-col overflow-hidden rounded-2xl bg-white shadow-2xl">
      <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
        <h3 class="flex items-center gap-2 text-xl font-bold text-slate-800">
          <span class="inline-block h-6 w-2 rounded-full bg-[#27c77a]"></span>
          預算試算
        </h3>
        <button @click="$emit('close')" class="p-1 text-slate-400 hover:text-slate-700">✕</button>
      </div>

      <div class="space-y-4 overflow-y-auto p-6">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-600">總預算 ({{ currency }})</label>
            <input
              v-model.number="form.totalBudget"
              type="number"
              min="0"
              class="w-full rounded-lg border border-slate-300 px-4 py-2 outline-none focus:border-[#27c77a] focus:ring-2 focus:ring-[#27c77a]/30"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-600">出遊人數</label>
            <input
              v-model.number="form.travelers"
              type="number"
              min="1"
              class="w-full rounded-lg border border-slate-300 px-4 py-2 outline-none focus:border-[#27c77a] focus:ring-2 focus:ring-[#27c77a]/30"
            />
          </div>
        </div>
        <p class="text-xs text-slate-400">天數：{{ form.days }} 天（依行程自動帶入）・付費景點：{{ spots.length }} 個</p>

        <button
          @click="runCalc"
          :disabled="loading"
          class="w-full rounded-lg bg-[#27c77a] py-2 font-bold text-white shadow transition hover:bg-[#1fb86d] disabled:opacity-60"
        >
          {{ loading ? '計算中...' : '計算分配' }}
        </button>

        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

        <!-- 結果 -->
        <div v-if="result" class="space-y-3">
          <div class="rounded-xl bg-slate-50 p-4">
            <div class="flex justify-between text-sm text-slate-600">
              <span>每人平均</span>
              <strong>{{ currency }} {{ formatNum(result.perPerson) }}</strong>
            </div>
          </div>

          <div
            v-for="row in breakdownRows"
            :key="row.key"
            class="flex items-center justify-between rounded-xl border border-slate-100 px-4 py-3"
          >
            <div class="flex items-center gap-2">
              <span>{{ row.icon }}</span>
              <span class="text-sm font-medium text-slate-700">{{ row.label }}</span>
              <span class="text-xs text-slate-400">{{ Math.round(row.ratio * 100) }}%</span>
            </div>
            <div class="text-right">
              <p class="font-bold text-slate-800">{{ currency }} {{ formatNum(row.total) }}</p>
              <p v-if="row.sub" class="text-xs text-slate-400">{{ row.sub }}</p>
            </div>
          </div>

          <div
            v-for="(w, i) in result.warnings"
            :key="i"
            class="rounded-lg bg-amber-50 px-4 py-2 text-sm text-amber-700"
          >
            ⚠️ {{ w }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { calculateBudget } from '../api/budget.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  trip: { type: Object, required: true },
})
defineEmits(['close'])

const currency = computed(() => props.trip?.budget || 'TWD')
const loading = ref(false)
const error = ref('')
const result = ref(null)

// 從行程 items 取出有票價的景點
const spots = computed(() => {
  const items = Object.values(props.trip?.itinerary || {}).flatMap((d) => d.items || [])
  return items
    .filter((it) => Number(it.ticketPrice) > 0)
    .map((it) => ({ name: it.title || it.name || '景點', ticketPrice: Number(it.ticketPrice) }))
})

const dayCount = computed(() => Object.keys(props.trip?.itinerary || {}).length || 1)

const form = reactive({ totalBudget: 60000, travelers: 1, days: dayCount.value })

// 開窗時重設天數並清空舊結果
watch(
  () => props.show,
  (open) => {
    if (open) {
      form.days = dayCount.value
      result.value = null
      error.value = ''
    }
  }
)

const runCalc = async () => {
  error.value = ''
  if (!form.totalBudget || form.totalBudget <= 0) {
    error.value = '請輸入有效的總預算'
    return
  }
  if (!form.travelers || form.travelers < 1) {
    error.value = '出遊人數至少 1 人'
    return
  }
  loading.value = true
  try {
    const res = await calculateBudget({
      totalBudget: form.totalBudget,
      days: form.days,
      travelers: form.travelers,
      spots: spots.value,
      currency: currency.value,
    })
    result.value = res.data
  } catch (err) {
    error.value = err?.response?.data?.error || '計算失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const formatNum = (n) => Number(n || 0).toLocaleString('en-US')

const breakdownRows = computed(() => {
  const b = result.value?.breakdown
  if (!b) return []
  return [
    { key: 'accommodation', icon: '🏨', label: '住宿', total: b.accommodation.total, ratio: b.accommodation.ratio, sub: `每人每晚 ${formatNum(b.accommodation.perPersonPerNight)}` },
    { key: 'food', icon: '🍜', label: '餐費', total: b.food.total, ratio: b.food.ratio, sub: `每人每日 ${formatNum(b.food.perPersonPerDay)}` },
    { key: 'transport', icon: '🚆', label: '交通', total: b.transport.total, ratio: b.transport.ratio, sub: '' },
    { key: 'activities', icon: '🎟', label: '活動/景點', total: b.activities.total, ratio: b.activities.ratio, sub: `票價合計 ${formatNum(b.activities.ticketTotal)}` },
    { key: 'emergency', icon: '🆘', label: '緊急備用', total: b.emergency.total, ratio: b.emergency.ratio, sub: '' },
  ]
})
</script>
