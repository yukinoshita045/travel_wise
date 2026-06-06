<template>
  <div class="border-t border-gray-200 bg-white p-3">
    <!-- 選擇式偏好面板（僅在對話開始時顯示） -->
    <div v-if="showStyleOptions" class="mb-3 space-y-3">
      <div v-for="group in PREFERENCE_GROUPS" :key="group.key">
        <p class="mb-1 text-xs font-semibold text-gray-600">{{ group.label }}</p>
        <div class="flex flex-wrap gap-2">
          <button
            v-for="opt in group.options"
            :key="opt"
            @click="toggleOption(group, opt)"
            :disabled="isLoading"
            class="px-3 py-1 rounded-full text-sm transition-colors disabled:opacity-40"
            :style="isSelected(group.key, opt)
              ? { backgroundColor: '#7E99BF', color: '#fff', border: '1px solid #7E99BF' }
              : { border: '1px solid #7E99BF', color: '#7E99BF' }"
          >
            {{ opt }}
          </button>
        </div>
      </div>

      <!-- 產生建議按鈕：把勾選結果組成訊息送出 -->
      <button
        @click="submitPreferences"
        :disabled="isLoading || !hasAnySelection"
        class="w-full rounded-xl py-2 text-sm text-white transition-colors disabled:opacity-40"
        style="background-color: #7E99BF;"
      >
        {{ isLoading ? '產生中...' : '產生行程建議' }}
      </button>
    </div>

    <!-- 文字輸入框（仍可自由補充） -->
    <div class="flex items-end gap-2">
      <textarea
        v-model="text"
        @keydown="handleKeyDown"
        :disabled="isLoading"
        rows="1"
        placeholder="Ask me anything..."
        class="flex-1 resize-none rounded-xl border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:border-gray-400 max-h-32"
      />
      <button
        @click="() => text.trim() && handleSend(text)"
        :disabled="!text.trim() || isLoading"
        class="p-2 rounded-xl text-white disabled:opacity-40 transition-colors"
        style="background-color: #94A3B8;"
      >
        {{ isLoading ? '...' : '➤' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'

// 偏好選項分組。single: true 表示該組為單選（例如高齡需求）
const PREFERENCE_GROUPS = [
  { key: 'interest', label: '興趣偏好', options: ['輕鬆休閒', '文化探索', '美食優先', '購物行程', '自然景觀', '歷史古蹟'] },
  { key: 'pace', label: '節奏偏好', options: ['悠閒', '一般', '緊湊'] },
  { key: 'accessibility', label: '高齡或行動不便需求', options: ['是', '否'], single: true },
  { key: 'transport', label: '交通偏好', options: ['步行', '大眾運輸', '自駕'] },
]

const props = defineProps({
  isLoading: Boolean,
  showStyleOptions: Boolean,
})

const emit = defineEmits(['send'])
const text = ref('')

// 各分組已勾選的選項（皆為陣列；單選組最多 1 個元素）
const selections = reactive({
  interest: [],
  pace: [],
  accessibility: [],
  transport: [],
})

const isSelected = (groupKey, opt) => selections[groupKey].includes(opt)

const toggleOption = (group, opt) => {
  const arr = selections[group.key]
  const idx = arr.indexOf(opt)
  if (group.single) {
    // 單選：再點同一個取消，點別的則取代
    selections[group.key] = idx === -1 ? [opt] : []
  } else {
    // 複選：累加 / 移除
    if (idx === -1) arr.push(opt)
    else arr.splice(idx, 1)
  }
}

const hasAnySelection = computed(() =>
  Object.values(selections).some((arr) => arr.length > 0)
)

// 把勾選結果組成一句自然語言，當作 message 送出（後端不需改動）
const buildMessage = () => {
  const parts = []
  if (selections.interest.length) parts.push(`想要${selections.interest.join('、')}類型的行程`)
  if (selections.pace.length) parts.push(`節奏${selections.pace.join('、')}`)
  if (selections.accessibility.includes('是')) parts.push('有高齡或行動不便需求')
  if (selections.transport.length) parts.push(`偏好${selections.transport.join('、')}交通`)
  return `我${parts.join('，')}。請幫我規劃行程。`
}

const submitPreferences = () => {
  if (props.isLoading || !hasAnySelection.value) return
  emit('send', buildMessage())
  // 送出後清空勾選
  Object.keys(selections).forEach((k) => { selections[k] = [] })
}

const handleSend = (content) => {
  if (props.isLoading) return
  emit('send', content)
  text.value = ''
}

const handleKeyDown = (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    if (text.value.trim()) handleSend(text.value)
  }
}
</script>