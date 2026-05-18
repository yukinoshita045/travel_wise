<template>
  <div class="border-t border-gray-200 bg-white p-3">
    <!-- 風格選項按鈕 -->
    <div v-if="showStyleOptions" class="flex flex-wrap gap-2 mb-3">
      <button
        v-for="option in STYLE_OPTIONS"
        :key="option"
        @click="handleSend(option)"
        :disabled="isLoading"
        class="px-3 py-1 rounded-full text-sm transition-colors disabled:opacity-40"
        style="border: 1px solid #7E99BF; color: #7E99BF;"
      >
        {{ option }}
      </button>
    </div>

    <!-- 文字輸入框 -->
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
import { ref } from 'vue'

const STYLE_OPTIONS = ['輕鬆休閒', '文化探索', '美食優先', '購物行程', '自然景觀', '歷史古蹟']

const props = defineProps({
  isLoading: Boolean,
  showStyleOptions: Boolean,
})

const emit = defineEmits(['send'])
const text = ref('')

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