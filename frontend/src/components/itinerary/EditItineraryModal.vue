<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  modelValue: Object,
  dayOptions: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits([
  'close',
  'submit',
])

const form = ref({
  day: '',
  time: '',
  title: '',
  location: '',
  address: '',
  stayTime: 0,
  description: '',
  image: '',
})

const inputClass =
  'w-full rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]'
const selectClass =
  `${inputClass} h-10 appearance-none bg-white px-2.5 pr-9 text-[#1E293B]`

watch(
  () => props.show,
  (val) => {
    if (val && props.modelValue) {
      form.value = {
        ...props.modelValue,
        day: props.modelValue.day || props.dayOptions[0]?.value || '',
        time: props.modelValue.time || '',
        stayTime: Number(props.modelValue.stayTime || 0),
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

  form.value.time = value
}

const handleUpdate = () => {
  if (!form.value.title.trim()) return

  const timeRegex = /^([01]\d|2[0-3]):[0-5]\d$/

  emit('submit', {
    ...form.value,
    day: form.value.day || props.modelValue?.day || props.dayOptions[0]?.value || '',
    time: timeRegex.test(form.value.time) ? form.value.time : '00:00',
    stayTime: Number(form.value.stayTime || 0),
  })
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
          v-if="form.image"
          :src="form.image"
          class="h-full w-full object-cover"
        />
      </div>

      <!-- FORM -->
      <div class="flex w-[55%] flex-col p-6">
        <h2 class="mb-4 text-xl font-bold text-[#1E293B]">
          編輯行程
        </h2>

        <div class="flex-1 space-y-4 overflow-y-auto">
          <!-- DAY / TIME -->
          <div class="grid grid-cols-[minmax(0,1.25fr)_minmax(120px,0.75fr)] gap-3">
            <div>
              <p class="mb-1 text-sm text-gray-400">
                天數 / 日期
              </p>

              <div class="relative">
                <select
                  v-model="form.day"
                  :class="selectClass"
                >
                  <option
                    v-for="option in dayOptions"
                    :key="option.value"
                    :value="option.value"
                  >
                    {{ option.label }}
                  </option>
                </select>
                <span class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400">
                  ▼
                </span>
              </div>
            </div>

            <div>
              <p class="mb-1 text-sm text-gray-400">
                開始時間
              </p>

              <input
                v-model="form.time"
                type="text"
                inputmode="numeric"
                maxlength="5"
                placeholder="09:00"
                :class="inputClass"
                @input="handleTimeInput"
              />
            </div>
          </div>

          <!-- TITLE -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              標題
            </p>

            <input
              v-model="form.title"
              :class="inputClass"
              placeholder="標題"
            />
          </div>

          <!-- LOCATION -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              地點
            </p>

            <input
              v-model="form.location"
              :class="inputClass"
              placeholder="地點"
            />
          </div>

          <!-- ADDRESS -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              地址
            </p>

            <input
              v-model="form.address"
              :class="inputClass"
              placeholder="地址"
            />
          </div>

          <!-- DESCRIPTION -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              描述
            </p>

            <textarea
              v-model="form.description"
              placeholder="描述"
              class="h-24 w-full resize-none rounded-xl border p-2 outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]"
            />
          </div>

          <!-- STAY TIME -->
          <div>
            <p class="mb-1 text-sm text-gray-400">
              停留時間
            </p>

            <div
              class="flex items-center justify-between rounded-xl border px-3 py-2 focus-within:border-[#94A3B8] focus-within:ring-0 focus-within:shadow-none"
            >
              <div class="flex items-center gap-3">
                <button
                  type="button"
                  @click="form.stayTime = Math.max(0, Number(form.stayTime || 0) - 0.5)"
                  class="h-8 w-8 rounded-full bg-gray-200"
                >
                  −
                </button>

                <span class="w-10 text-center text-sm text-gray-500">
                  {{ form.stayTime }}
                </span>

                <button
                  type="button"
                  @click="form.stayTime = Number(form.stayTime || 0) + 0.5"
                  class="h-8 w-8 rounded-full bg-[#94A3B8] text-white"
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
            @click="handleUpdate"
            class="flex-1 rounded-xl bg-[#94A3B8] py-2 text-white"
          >
            儲存
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
