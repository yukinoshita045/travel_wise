<script setup>
import { ShoppingBag,  } from 'lucide-vue-next'

defineProps({
  size: {
    type: String,
    default: 'md',
  },
})

const emit = defineEmits(['click'])

const sizeClass = {
  sm: 'h-9 w-9',
  md: 'h-11 w-11',
  lg: 'h-12 w-12',
}

const iconClass = {
  sm: 'h-4 w-4',
  md: 'h-5 w-5',
  lg: 'h-6 w-6',
}
</script>

<template>
  <button
    type="button"
    @click="emit('click')"
    :class="[
      'flex items-center justify-center rounded-full bg-white text-[#64748B] shadow-sm transition hover:bg-gray-50 hover:opacity-90',
      sizeClass[size],
    ]"
  >
    <ShoppingBag :class="iconClass[size]" />
  </button>
</template>