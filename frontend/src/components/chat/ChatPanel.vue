<template>
  <!-- 關閉狀態 -->
  <button
    v-if="panelState === 'closed'"
    @click="panelState = 'half'"
    class="fixed bottom-6 left-6 text-white px-4 py-2 rounded-full shadow-lg transition-colors z-50"
    style="background-color: #7E99BF;"
  >
    AI 行程建議
  </button>

  <!-- 全開狀態 -->
  <div
    v-else-if="panelState === 'full'"
    class="fixed inset-0 bg-white z-50 flex flex-col"
  >
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
      <span class="font-semibold text-gray-700">AI 行程建議</span>
      <div class="flex items-center gap-1">
        <button
          @click="panelState = 'closed'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="縮小"
        >─</button>
        <button
          @click="panelState = 'half'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="縮小視窗"
        >❐</button>
        <button
          @click="panelState = 'closed'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="關閉"
        >✕</button>
      </div>
    </div>
    <ChatWindow :messages="messages" />
    <ChatInput
      :isLoading="isLoading"
      :showStyleOptions="messages.length === 0"
      @send="handleSend"
    />
  </div>

  <!-- 半開狀態 -->
  <div
    v-else
    class="fixed top-0 left-0 h-full bg-white shadow-xl z-40 flex flex-col"
    :style="{ width: panelWidth + 'px' }"
  >
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
      <span class="font-semibold text-gray-700">AI 行程建議</span>
      <div class="flex items-center gap-1">
        <button
          @click="panelState = 'closed'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="縮小"
        >─</button>
        <button
          @click="panelState = 'full'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="最大化"
        >❐</button>
        <button
          @click="panelState = 'closed'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="關閉"
        >✕</button>
      </div>
    </div>
    <ChatWindow :messages="messages" />
    <ChatInput
      :isLoading="isLoading"
      :showStyleOptions="messages.length === 0"
      @send="handleSend"
    />
    <!-- 拖拉條 -->
    <div
      @mousedown="handleMouseDown"
      class="absolute top-0 right-0 w-1 h-full cursor-col-resize hover:bg-gray-300 transition-colors"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import ChatWindow from './ChatWindow.vue'
import ChatInput from './ChatInput.vue'
import { sendChat } from '../../api/trip'

const props = defineProps({ tripId: String })

const panelState = ref('closed')
const messages = ref([])
const isLoading = ref(false)
const panelWidth = ref(400)
const isDragging = ref(false)

const handleSend = async (content) => {
  messages.value.push({ role: 'user', content })
  isLoading.value = true

  try {
    const response = await sendChat({
      message: content,
      conversationId: null,
      tripParams: { destination: 'Tokyo', days: 3, travelers: 1 },
    })
    messages.value.push({
      role: 'assistant',
      content: response.data.message || '收到你的需求，以下是建議...',
    })
  } catch {
    messages.value.push({ role: 'assistant', content: '發生錯誤，請稍後再試。' })
  } finally {
    isLoading.value = false
  }
}

const handleMouseDown = () => {
  isDragging.value = true
  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}

const handleMouseMove = (e) => {
  if (!isDragging.value) return
  const newWidth = e.clientX
  if (newWidth > 250 && newWidth < window.innerWidth - 200) {
    panelWidth.value = newWidth
  }
}

const handleMouseUp = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', handleMouseMove)
  document.removeEventListener('mouseup', handleMouseUp)
}
</script>