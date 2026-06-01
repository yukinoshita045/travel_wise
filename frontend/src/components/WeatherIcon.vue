<script setup>
import { computed } from 'vue'
import {
  Cloud,
  CloudRain,
  CloudSnow,
  CloudSun,
  Sun,
  Wind,
} from 'lucide-vue-next'

const props = defineProps({
  weather: {
    type: String,
    default: '',
  },
  sizeClass: {
    type: String,
    default: 'h-7 w-7',
  },
})

const iconComponent = computed(() => {
  const weather = props.weather

  if (weather.includes('雪') || weather.includes('❄')) return CloudSnow
  if (weather.includes('雨') || weather.includes('☔')) return CloudRain
  if (weather.includes('風') || weather.includes('🌬')) return Wind
  if (weather.includes('雲') || weather.includes('陰') || weather.includes('🌥')) return CloudSun
  if (weather.includes('☀') || weather.includes('晴')) return Sun

  return Cloud
})
</script>

<template>
  <component
    :is="iconComponent"
    :class="['text-[#7E99BF]', sizeClass]"
    :stroke-width="2"
  />
</template>
