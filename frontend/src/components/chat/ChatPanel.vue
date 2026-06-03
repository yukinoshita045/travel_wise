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
        <!-- 縮小：full → half -->
        <button
          @click="panelState = 'half'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="縮小"
        >─</button>
        <!-- 中間格：full 顯示雙方框，點了還原回 half -->
        <button
          @click="panelState = 'half'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="還原"
        >❐</button>
        <!-- 關閉：收起並清空對話 -->
        <button
          @click="closePanel"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="關閉"
        >✕</button>
      </div>
    </div>
    <ChatWindow :messages="messages" :isLoading="isLoading" @add-spot="(spot) => emit('add-spot', spot)" />
    <ChatInput
      :isLoading="isLoading"
      :showStyleOptions="messages.length === 0"
      @send="handleSend"
    />
  </div>

  <!-- 半開狀態 -->
  <div
    v-else
    class="fixed left-0 top-16 bottom-0 bg-white shadow-xl z-30 flex flex-col"
    :style="{ width: panelWidth + 'px' }"
  >
    <div class="flex items-center justify-between px-4 py-3 border-b border-gray-200">
      <span class="font-semibold text-gray-700">AI 行程建議</span>
      <div class="flex items-center gap-1">
        <!-- 縮小：half → closed（保留對話） -->
        <button
          @click="panelState = 'closed'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="縮小"
        >─</button>
        <!-- 中間格：half 顯示單方框，點了最大化到 full -->
        <button
          @click="panelState = 'full'"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="最大化"
        >□</button>
        <!-- 關閉：收起並清空對話 -->
        <button
          @click="closePanel"
          class="w-6 h-6 flex items-center justify-center rounded hover:bg-gray-100 text-gray-400 text-xs"
          title="關閉"
        >✕</button>
      </div>
    </div>
    <ChatWindow :messages="messages" :isLoading="isLoading" @add-spot="(spot) => emit('add-spot', spot)" />
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
import { ref, watch, computed } from 'vue'
import ChatWindow from './ChatWindow.vue'
import ChatInput from './ChatInput.vue'
import { sendChat } from '../../api/trip'
import { getTripOrDefault } from '../../data/travelStore'

const props = defineProps({ tripId: String })
const emit = defineEmits(['layout-change', 'add-spot'])

const panelState = ref('closed')
const messages = ref([])
const isLoading = ref(false)
const panelWidth = ref(400)
const isDragging = ref(false)
const conversationId = ref(null)

// 取當前旅程的真實資料，傳給 AI 作為上下文
const trip = computed(() => getTripOrDefault(props.tripId))

const getTripParams = () => {
  const t = trip.value
  if (!t) return { destination: '未知', days: 3, travelers: 1 }
  const dayCount = t.dates?.match(/共(\d+)天/)?.[1] || 3
  return {
    destination: t.destination || t.title,
    days: Number(dayCount),
    travelers: 1,
    startDate: t.startDate,
    endDate: t.endDate,
  }
}

// 關閉：收起面板並清空對話紀錄（與「縮小」區分）
const closePanel = () => {
  panelState.value = 'closed'
  messages.value = []
  conversationId.value = null
}

/** 把 AI 回傳的 reply 轉成 { text, spots }；text 供顯示，spots 供「加入行程」 */
const formatReply = (reply) => {
  if (!reply) return { text: '收到你的需求，以下是建議...', spots: [] }

  // 行程 JSON 格式：保留結構化 spots
  if (reply.type === 'itinerary' && reply.content?.days) {
    const days = reply.content.days
    const title = reply.content.title || '行程建議'
    let text = `**${title}**\n\n`
    const spots = []
    days.forEach((day) => {
      text += `📅 Day ${day.dayNumber}${day.theme ? `：${day.theme}` : ''}\n`
      ;(day.spots || []).forEach((spot) => {
        text += `  🕐 ${spot.arrivalTime}  **${spot.name}**\n`
        if (spot.description) text += `     ${spot.description}\n`
        if (spot.notes) text += `     💡 ${spot.notes}\n`
        text += '\n'
        spots.push({
          arrivalTime: spot.arrivalTime,
          name: spot.name,
          description: spot.description || '',
          notes: spot.notes || '',
        })
      })
    })
    return { text, spots }
  }

  // 純文字回覆：沒有可加入的 spots
  if (typeof reply.content === 'string') return { text: reply.content, spots: [] }
  if (typeof reply === 'string') return { text: reply, spots: [] }

  return { text: '收到你的需求，以下是建議...', spots: [] }
}

watch(
  [panelState, panelWidth],
  ([state, width]) => {
    emit('layout-change', {
      isOpen: state === 'half',
      width: state === 'half' ? width : 0,
    })
  },
  { immediate: true }
)

const handleSend = async (content) => {
  // ───────────────────────────────────────────────
  // 【臨時測試用，OpenAI key 修好後請刪掉這整段】
  // 用來在沒有 AI 回應時，驗證結構化卡片渲染與「加入行程」功能
  messages.value.push({
    role: 'assistant',
    content: '**測試行程**',
    spots: [
      { arrivalTime: '09:00', name: '測試景點A', description: '說明A', notes: '提示A' },
      { arrivalTime: '11:00', name: '測試景點B', description: '說明B', notes: '' },
    ],
  })
  return
  // ───────────────────────────────────────────────

  messages.value.push({ role: 'user', content })
  isLoading.value = true

  try {
    const response = await sendChat({
      message: content,
      conversationId: conversationId.value,
      tripParams: getTripParams(),
    })

    const data = response.data
    // 保留 conversationId 維持對話連貫
    if (data.conversationId) conversationId.value = data.conversationId

    const replyText = formatReply(data.reply)
    messages.value.push({
      role: 'assistant',
      content: replyText.text,
      spots: replyText.spots,   // 結構化 spots，供 ChatBubble 渲染加號卡片
    })
  } catch (err) {
    console.error('[ChatPanel] API error:', err)
    messages.value.push({ role: 'assistant', content: '⚠️ 發生錯誤，請稍後再試。' })
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