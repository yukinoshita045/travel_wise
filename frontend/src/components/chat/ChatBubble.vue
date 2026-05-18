<template>
  <div :class="['flex mb-3', isUser ? 'justify-end' : 'justify-start']">
    <div :class="['max-w-[75%] px-4 py-2 rounded-2xl text-sm', isUser
      ? 'text-white rounded-br-sm'
      : 'bg-white text-gray-800 rounded-bl-sm shadow-sm']"
      :style="isUser ? { backgroundColor: '#7E99BF' } : {}"
    >
      {{ message.content }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  message: Object,
})

const isUser = computed(() => props.message.role === 'user')
</script>