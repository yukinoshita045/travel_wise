<template>
  <div class="flex-1 overflow-y-auto px-4 py-3 bg-gray-50" ref="bottomRef">
    <div v-if="messages.length === 0" class="text-center text-gray-400 text-sm mt-8">
      選擇風格或輸入問題，讓 TravelWIse AI 建議今日行程！
    </div>
    <ChatBubble
      v-for="(msg, index) in messages"
      :key="index"
      :message="msg"
      @add-spot="(spot) => $emit('add-spot', spot)"
    />

    <!-- 載入中：AI 思考泡泡（三點跳動），靠左對齊與 AI 泡泡一致 -->
    <div v-if="isLoading" class="flex justify-start mb-3">
      <div class="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm flex gap-1.5 items-center">
        <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0ms"></span>
        <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 150ms"></span>
        <span class="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 300ms"></span>
      </div>
    </div>

    <div ref="bottom" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import ChatBubble from './ChatBubble.vue'

const props = defineProps({
  messages: Array,
  isLoading: Boolean,
})

defineEmits(['add-spot'])

const bottom = ref(null)

watch(
  () => [props.messages, props.isLoading],
  async () => {
    await nextTick()
    bottom.value?.scrollIntoView({ behavior: 'smooth' })
  },
  { deep: true }
)
</script>