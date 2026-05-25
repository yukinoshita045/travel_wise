<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  form: Object,
})

const emit = defineEmits(['close', 'submit', 'update:form'])

const fileInputRef = ref(null)

const localForm = ref({
  time: '',
  title: '',
  location: '',
  address: '',
  stayTime: 0,
  description: '',
  image: '',
})

watch(
  () => props.show,
  (val) => {
    if (val) {
      localForm.value = {
        time: '',
        title: '',
        location: '',
        address: '',
        stayTime: 0,
        description: '',
        image: '',
      }
    }
  }
)

const handleTimeInput = (e) => {
  let value = e.target.value.replace(/\D/g, '')

  value = value.slice(0, 4)

  if (value.length >= 3) {
    value = `${value.slice(0, 2)}:${value.slice(2)}`
  }

  localForm.value.time = value
}

const handleImageUpload = (e) => {
  const file = e.target.files?.[0]
  if (!file) return

  localForm.value.image = URL.createObjectURL(file)
}

const handleSubmit = () => {
  const timeRegex = /^([01]\d|2[0-3]):[0-5]\d$/

  const payload = {
    time: timeRegex.test(localForm.value.time)
      ? localForm.value.time
      : '00:00',
    title: localForm.value.title,
    location: localForm.value.location,
    address: localForm.value.address,
    stayTime: Number(localForm.value.stayTime || 0),
    description: localForm.value.description,
    image: localForm.value.image,
  }

  emit('submit', payload)
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    @click="handleClose"
  >
    <div
      class="flex w-[760px] overflow-hidden rounded-3xl bg-white shadow-xl"
      @click.stop
    >
      <!-- IMAGE -->
      <div class="relative flex w-[45%] items-center justify-center bg-gray-100">
        <img
          v-if="localForm.image"
          :src="localForm.image"
          class="h-full w-full object-cover"
        />

        <p v-else class="text-gray-400">
          尚未選擇圖片
        </p>

        <button
          type="button"
          @click="fileInputRef?.click()"
          class="absolute bottom-4 left-1/2 -translate-x-1/2 rounded-full bg-[#94A3B8] px-4 py-2 text-sm text-white"
        >
          上傳圖片
        </button>

        <input
          ref="fileInputRef"
          type="file"
          accept="image/*"
          class="hidden"
          @change="handleImageUpload"
        />
      </div>

      <!-- FORM -->
      <div class="flex w-[55%] flex-col p-6">
        <h2 class="mb-4 text-xl font-bold text-[#1E293B]">
          新增行程
        </h2>

        <div class="flex-1 space-y-4 overflow-y-auto">
          <!-- TIME -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              開始時間
            </p>

            <input
              v-model="localForm.time"
              type="text"
              inputmode="numeric"
              maxlength="5"
              placeholder="00:00"
              class="w-full rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]"
              @input="handleTimeInput"
            />
<!-- 
            <p class="mt-1 text-xs text-gray-400">
              請輸入 4 位數，例如 0900 會自動轉成 09:00
            </p> -->
          </div>

          <!-- TITLE -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              標題
            </p>

            <input
              v-model="localForm.title"
              class="w-full rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]"
            />
          </div>

          <!-- LOCATION -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              地點
            </p>

            <input
              v-model="localForm.location"
              class="w-full rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]"
            />
          </div>

          <!-- ADDRESS -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              地址
            </p>

            <input
              v-model="localForm.address"
              class="w-full rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]"
            />
          </div>

          <!-- DESCRIPTION -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              描述
            </p>

            <textarea
              v-model="localForm.description"
              class="w-full rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8] resize-none"
            />
          </div>

          <!-- STAY TIME -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              停留時間
            </p>

            <div class="flex items-center justify-between rounded-xl border px-3 py-2 focus-within:border-[#94A3B8]">              <div class="flex items-center gap-3">
                <button
                  type="button"
                  @click="localForm.stayTime = Math.max(0, Number(localForm.stayTime || 0) - 0.5)"
                  class="h-10 w-10 rounded-full bg-gray-200 text-xl font-bold"
                >
                  −
                </button>

                <span class="w-10 text-center text-sm text-gray-500">
                  {{ localForm.stayTime }}
                </span>

                <button
                  type="button"
                  @click="localForm.stayTime = Number(localForm.stayTime || 0) + 0.5"
                  class="h-10 w-10 rounded-full bg-[#94A3B8] text-xl font-bold text-white"
                >
                  +
                </button>
              </div>

              <div class="text-sm text-gray-400">
                小時
              </div>
            </div>
          </div>
        </div>

        <!-- BUTTONS -->
        <div class="mt-4 flex gap-3">
          <button
            type="button"
            @click="handleClose"
            class="flex-1 rounded-xl bg-gray-200 py-2"
          >
            取消
          </button>

          <button
            type="button"
            @click="handleSubmit"
            class="flex-1 rounded-xl bg-[#94A3B8] py-2 text-white"
          >
            新增
          </button>
        </div>
      </div>
    </div>
  </div>
</template>