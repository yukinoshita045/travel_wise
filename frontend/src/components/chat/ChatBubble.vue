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

      <!-- AI 回覆：支援換行 + **粗體** -->
      <div v-else class="leading-relaxed whitespace-pre-wrap break-words">
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

        <!-- Task 2：結構化行程建議卡片，每張可單獨加入 -->
        <div v-if="spots.length" class="mt-3 space-y-2">
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
            <!-- 加號：加入當前選取日的行程 -->
            <button
              @click="$emit('add-spot', spot)"
              class="shrink-0 h-7 w-7 rounded-full text-white flex items-center justify-center"
              style="background-color: #7E99BF;"
              title="加入行程"
            >+</button>
          </div>
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

// 結構化行程 spots（沒有則為空陣列，不渲染卡片）
const spots = computed(() => props.message.spots || [])

/** 把文字按行分割，並解析每行中的 **粗體** 區段 */
const formattedLines = computed(() => {
  const raw = props.message.content || ''
  return raw.split('\n').map((line) => {
    if (line.trim() === '') return { isBlank: true, segments: [] }

    // 解析 **text** → { text, bold }
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