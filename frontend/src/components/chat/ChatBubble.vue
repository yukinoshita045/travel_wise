<template>
  <div :class="['flex mb-3', isUser ? 'justify-end' : 'justify-start']">
    <div
      :class="['max-w-[75%] px-4 py-2 rounded-2xl text-sm', isUser
        ? 'text-white rounded-br-sm'
        : 'bg-white text-gray-800 rounded-bl-sm shadow-sm']"
      :style="isUser ? { backgroundColor: '#7E99BF' } : {}"
    >
      <!-- 使用者訊息：純文字 -->
      <span v-if="isUser">{{ message.content }}</span>

      <!-- AI 回覆 -->
      <div v-else class="leading-relaxed break-words">
        <!-- 有卡片時：只顯示標題 + 卡片（不顯示逐行文字） -->
        <template v-if="spots.length">
          <p v-if="displayTitle" class="mb-2 font-semibold">{{ displayTitle }}</p>
          <div class="space-y-2">
            <div
              v-for="(spot, k) in spots"
              :key="k"
              class="flex items-start gap-2 rounded-2xl bg-[#F8FAFC] p-3"
            >
              <div class="flex-1">
                <div class="flex items-baseline gap-2">
                  <span class="text-xs text-[#64748B]">{{ spot.arrivalTime }}</span>
                  <span class="font-semibold text-[#1E293B]">{{ spot.name }}</span>
                </div>
                <p v-if="spot.description" class="mt-1 text-xs text-gray-600">
                  {{ spot.description }}
                </p>
                <p v-if="spot.notes" class="mt-1 text-xs text-gray-500">
                  💡 {{ spot.notes }}
                </p>
              </div>
              <button
                @click="$emit('add-spot', spot)"
                class="shrink-0 h-7 w-7 rounded-full text-white flex items-center justify-center"
                style="background-color: #7E99BF;"
                title="加入行程"
              >+</button>
            </div>
          </div>
        </template>

        <!-- 無卡片時（純文字對話）：照原本的換行 + 粗體渲染 -->
        <div v-else class="whitespace-pre-wrap">
          <template v-for="(line, i) in formattedLines" :key="i">
            <div :class="line.isBlank ? 'h-2' : ''">
              <template v-if="!line.isBlank">
                <span
                  v-for="(seg, j) in line.segments"
                  :key="j"
                  :class="seg.bold ? 'font-semibold' : ''"
                >{{ seg.text }}</span>
              </template>
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: Object,
})

defineEmits(['add-spot'])

const isUser = computed(() => props.message.role === 'user')

// 結構化行程 spots（沒有則為空陣列）
const spots = computed(() => props.message.spots || [])

// 從 AI 回覆文字抽出第一行標題（去掉 ** 符號），供有卡片時顯示
const displayTitle = computed(() => {
  const raw = props.message.content || ''
  const firstLine = raw.split('\n').find((l) => l.trim() !== '') || ''
  return firstLine.replace(/\*\*/g, '').trim()
})

/** 把文字按行分割，並解析每行中的 **粗體** 區段（純文字對話時使用） */
const formattedLines = computed(() => {
  const raw = props.message.content || ''
  return raw.split('\n').map((line) => {
    if (line.trim() === '') return { isBlank: true, segments: [] }
    const segments = []
    const regex = /\*\*(.+?)\*\*/g
    let last = 0
    let match
    while ((match = regex.exec(line)) !== null) {
      if (match.index > last) segments.push({ text: line.slice(last, match.index), bold: false })
      segments.push({ text: match[1], bold: true })
      last = match.index + match[0].length
    }
    if (last < line.length) segments.push({ text: line.slice(last), bold: false })
    return { isBlank: false, segments }
  })
})
</script>