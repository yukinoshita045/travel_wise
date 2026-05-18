<template>
  <div class="flex-1 overflow-y-auto px-4 py-3 bg-gray-50" ref="bottomRef">
    <div v-if="messages.length === 0" class="text-center text-gray-400 text-sm mt-8">
      選擇風格或輸入問題，讓 TravelWIse AI 建議今日行程！
    </div>
    <ChatBubble
      v-for="(msg, index) in messages"
      :key="index"
      :message="msg"
    />
    <div ref="bottom" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import ChatBubble from './ChatBubble.vue'

const props = defineProps({
  messages: Array,
})

const bottom = ref(null)

watch(() => props.messages, async () => {
  await nextTick()
  bottom.value?.scrollIntoView({ behavior: 'smooth' })
})
</script>