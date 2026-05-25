<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  item: Object,
  date: String,
})

const emit = defineEmits([
  'close',
  'edit',
  'add-prep-item',
])

const showPrepModal = ref(false)

const handleClose = () => {
  emit('close')
}

const handleEdit = () => {
  emit('edit', props.item)
}


</script>

<template>
  <div
    v-if="item"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click="handleClose"
  >
    <!-- LARGE MODAL -->
    <div
      class="flex h-[520px] w-[900px] overflow-hidden rounded-3xl bg-white shadow-2xl"
      @click.stop
    >
      <!-- LEFT IMAGE -->
      <div class="w-[45%]">
        <img
          :src="item.image"
          class="h-full w-full object-cover"
        />
      </div>

      <!-- RIGHT CONTENT -->
      <div class="relative flex flex-1 flex-col p-6">
        <!-- TOP BAR -->
        <div class="flex items-start justify-between gap-4">
          <!-- LEFT TEXT -->
          <div class="min-w-0 flex-1">
            <h2 class="text-xl font-bold leading-tight text-[#1E293B]">
              {{ item.title }}
            </h2>

            <p class="mt-1 text-sm leading-snug text-gray-500">
              {{ item.location }}
            </p>

            <p class="mt-1 line-clamp-2 text-xs leading-relaxed text-gray-400">
              {{ item.address }}
            </p>
          </div>

          <!-- EDIT BUTTON -->
          <div class="flex-shrink-0 pt-1">
            <button
              @click="handleEdit"
              class="whitespace-nowrap rounded-xl bg-[#94A3B8] px-4 py-2 text-xs font-medium text-white shadow-sm hover:opacity-90"
            >
              編輯行程
            </button>
          </div>
        </div>

        <!-- DESCRIPTION -->
        <div class="mt-6">
          <p class="text-sm leading-relaxed text-gray-600">
            {{ item.description }}
          </p>
        </div>


        <!-- FOOTER -->
        <div class="absolute bottom-6 right-6 text-sm text-[#64748B]">
          停留 {{ item.stayTime }} 小時
        </div>
      </div>
    </div>

  </div>
</template>