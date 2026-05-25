<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  dayOptions: Array,
  categoryOptions: Array,
})

const emit = defineEmits([
  'close',
  'submit',
])

const form = ref({
  name: '',
  day: '',
  category: '',
})

const errorMessage = ref('')

watch(
  () => props.show,
  (newVal) => {
    if (newVal) {
      form.value = {
        name: '',
        day: '',
        category: '',
      }

      errorMessage.value = ''
    }
  }
)
const handleSubmit = () => {
  if (
    !form.value.name.trim() ||
    !form.value.day ||
    !form.value.category.trim()
  ) {
    errorMessage.value = '請完整填寫所有資訊'
    return
  }

  errorMessage.value = ''

  emit('submit', {
    ...form.value,
  })
}

const handleClose = () => {
  emit('close')
}
</script>

<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40"
    @click="handleClose"
  >
    <div
      class="w-[420px] rounded-3xl bg-white p-6 shadow-xl"
      @click.stop
    >
      <h2 class="mb-5 text-xl font-bold text-[#1E293B]">
        新增物品
      </h2>

      <div class="space-y-4">

        <!-- Name -->
        <div>
          <p class="mb-2 text-sm text-gray-500">
            物品名稱
          </p>

          <input
            v-model="form.name"
            type="text"
            class="h-12 w-full rounded-xl border border-gray-200 px-2 placeholder:text-gray-400"
            placeholder="輸入物品名稱"
          />
        </div>

        <!-- Day -->
        <div>
          <p class="mb-2 text-sm text-gray-500">
            日期
          </p>

          <select
            v-model="form.day"
            :class="[
            'h-12 w-full rounded-xl border border-gray-200 px-4 outline-none',
            form.day
                ? 'text-gray-800'
                : 'text-gray-400'
            ]"
            required
          >
            <option disabled value="">
              請選擇日期
            </option>

            <option
              v-for="item in dayOptions"
              :key="item.day"
              :value="item.day"
            >
              {{ item.day }} · {{ item.date }}
            </option>
          </select>
        </div>

        <!-- Category -->
        <div>
          <p class="mb-2 text-sm text-gray-500">
            類型
          </p>

          <input
            v-model="form.category"
            list="category-options"
            class="h-12 w-full rounded-xl border border-gray-200 px-2 placeholder:text-gray-400"
            placeholder="選擇或輸入類型"
          />

          <datalist id="category-options">
            <option
              v-for="c in categoryOptions"
              :key="c"
              :value="c"
            />
          </datalist>
        </div>

      </div>

      <!-- Error Message -->
      <p
        v-if="errorMessage"
        class="mt-4 text-sm text-red-500"
      >
        {{ errorMessage }}
      </p>


      <!-- Buttons -->
      <div class="mt-6 flex gap-3">

        <button
          @click="handleClose"
          class="flex-1 rounded-xl bg-gray-200 py-3 text-gray-700"
        >
          取消
        </button>

        <button
          @click="handleSubmit"
          class="flex-1 rounded-xl bg-[#94A3B8] py-3 text-white"
        >
          新增
        </button>

      </div>

    </div>
  </div>
</template>

