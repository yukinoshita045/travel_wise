<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm"
    @click.self="$emit('close')"
  >
    <div class="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl">
      <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
        <h3 class="flex items-center gap-2 text-xl font-bold text-slate-800">
          <span class="inline-block h-6 w-2 rounded-full bg-[#7E99BF]"></span>
          匯率換算
        </h3>
        <button @click="$emit('close')" class="p-1 text-slate-400 hover:text-slate-700">✕</button>
      </div>

      <div class="space-y-4 p-6">
        <div>
          <label class="mb-1 block text-sm font-medium text-slate-600">金額</label>
          <input
            v-model.number="amount"
            type="number"
            min="0"
            class="w-full rounded-lg border border-slate-300 px-4 py-2 outline-none focus:border-[#7E99BF] focus:ring-2 focus:ring-[#7E99BF]/40"
          />
        </div>

        <div class="flex items-end gap-3">
          <div class="flex-1">
            <label class="mb-1 block text-sm font-medium text-slate-600">從</label>
            <select v-model="from" class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 outline-none focus:border-[#7E99BF]">
              <option v-for="(name, code) in currencies" :key="code" :value="code">{{ code }} {{ name }}</option>
            </select>
          </div>
          <button @click="swap" class="mb-1 rounded-lg bg-slate-100 px-3 py-2 text-slate-500 hover:bg-slate-200" title="對調">⇄</button>
          <div class="flex-1">
            <label class="mb-1 block text-sm font-medium text-slate-600">到</label>
            <select v-model="to" class="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 outline-none focus:border-[#7E99BF]">
              <option v-for="(name, code) in currencies" :key="code" :value="code">{{ code }} {{ name }}</option>
            </select>
          </div>
        </div>

        <button
          @click="runConvert"
          :disabled="loading"
          class="w-full rounded-lg bg-[#7E99BF] py-2 font-bold text-white shadow transition hover:opacity-90 disabled:opacity-60"
        >
          {{ loading ? '換算中...' : '換算' }}
        </button>

        <p v-if="error" class="text-sm text-red-500">{{ error }}</p>

        <div v-if="result" class="rounded-xl bg-slate-50 p-4 text-center">
          <p class="text-sm text-slate-500">{{ formatNum(result.amount) }} {{ result.from }} =</p>
          <p class="mt-1 text-2xl font-bold text-[#7E99BF]">{{ formatNum(result.converted) }} {{ result.to }}</p>
          <p class="mt-1 text-xs text-slate-400">匯率 1 {{ result.from }} = {{ result.rate }} {{ result.to }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { fetchRates, convertCurrency, inferCurrencyFromDestination } from '../api/currency.js'

const props = defineProps({
  show: { type: Boolean, default: false },
  trip: { type: Object, required: true },
})
defineEmits(['close'])

const amount = ref(1000)
const from = ref('TWD')
const to = ref('JPY')
const currencies = ref({ TWD: '新台幣', JPY: '日圓', USD: '美元' })
const loading = ref(false)
const error = ref('')
const result = ref(null)

// 開窗時載入支援幣別清單，並依目的地預設目標幣別
watch(
  () => props.show,
  async (open) => {
    if (!open) return
    error.value = ''
    result.value = null
    const inferred = inferCurrencyFromDestination(props.trip?.destination || '')
    if (inferred) to.value = inferred
    try {
      const res = await fetchRates('TWD')
      if (res.data?.supportedCurrencies) currencies.value = res.data.supportedCurrencies
    } catch {
      // 載入失敗時沿用預設清單
    }
  }
)

const swap = () => {
  const t = from.value
  from.value = to.value
  to.value = t
  result.value = null
}

const runConvert = async () => {
  error.value = ''
  if (amount.value == null || amount.value < 0) {
    error.value = '請輸入有效金額'
    return
  }
  loading.value = true
  try {
    const res = await convertCurrency(amount.value, from.value, to.value)
    result.value = res.data
  } catch (err) {
    error.value = err?.response?.data?.error || '換算失敗，請稍後再試'
  } finally {
    loading.value = false
  }
}

const formatNum = (n) => Number(n || 0).toLocaleString('en-US')
</script>
