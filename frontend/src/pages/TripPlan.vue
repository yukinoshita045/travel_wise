<template>
  <div class="min-h-screen bg-[#F8FAFC] pt-24">
    <Navbar />
    <ChatPanel :tripId="tripId" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import ChatPanel from '../components/chat/ChatPanel.vue'

const route = useRoute()
const tripId = computed(() => route.params.id)
</script>
