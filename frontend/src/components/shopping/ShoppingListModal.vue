<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  show: Boolean,
  modelValue: {
    type: Array,
    default: () => [],
  },
})

const emit = defineEmits([
  'close',
  'update:modelValue',
])

const newItemName = ref('')
const editingIndex = ref(null)
const editingText = ref('')

const inputClass =
  'w-full border-b border-gray-300 bg-transparent px-1 py-2 text-sm outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]'

const localItems = ref([])

watch(
  () => props.show,
  (val) => {
    if (val) {
      localItems.value = props.modelValue.map((item) => ({ ...item }))
      newItemName.value = ''
      editingIndex.value = null
      editingText.value = ''
    }
  }
)

const syncItems = () => {
  emit('update:modelValue', localItems.value)
}

const addItem = () => {
  const name = newItemName.value.trim()
  if (!name) return

  localItems.value.push({
    name,
    checked: false,
  })

  newItemName.value = ''
  syncItems()
}

const toggleItem = (index) => {
  localItems.value[index].checked = !localItems.value[index].checked
  syncItems()
}

const startEdit = (index) => {
  editingIndex.value = index
  editingText.value = localItems.value[index].name
}

const saveEdit = () => {
  if (editingIndex.value === null) return

  const name = editingText.value.trim()
  if (!name) return

  localItems.value[editingIndex.value].name = name

  editingIndex.value = null
  editingText.value = ''
  syncItems()
}

const cancelEdit = () => {
  editingIndex.value = null
  editingText.value = ''
}

const deleteItem = (index) => {
  localItems.value.splice(index, 1)
  syncItems()
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
      class="flex h-[430px] w-[420px] flex-col rounded-3xl bg-white p-6 shadow-xl"
      @click.stop
    >
      <!-- Header -->
      <div class="mb-4 flex items-center justify-between">
        <div>
          <h2 class="text-lg font-bold text-[#1E293B]">
            購物清單
          </h2>
          <p class="mt-1 text-sm text-gray-400">
            勾選已購買的物品
          </p>
        </div>

        <button
          type="button"
          @click="handleClose"
          class="rounded-full px-3 py-1 text-gray-400 hover:bg-gray-100"
        >
          ✕
        </button>
      </div>

      <!-- List -->
      <div class="flex-1 overflow-y-auto pr-1 space-y-3">
        <div
          v-for="(item, index) in localItems"
          :key="index"
          class="group flex items-center justify-between rounded-2xl border border-gray-100 bg-gray-50 px-4 py-3 transition hover:bg-gray-100"
        >
          <!-- Normal mode -->
          <template v-if="editingIndex !== index">
            <div class="min-w-0 flex-1">
              <p
                :class="[
                  'truncate text-sm font-medium text-gray-800',
                  item.checked ? 'text-gray-400 line-through' : ''
                ]"
              >
                {{ item.name }}
              </p>
            </div>

            <div class="ml-3 flex items-center gap-2">
              <button
                type="button"
                @click="startEdit(index)"
                class="hidden text-xs text-gray-400 hover:text-[#64748B] group-hover:block"
              >
                刪除
              </button>

              <button
                type="button"
                @click="deleteItem(index)"
                class="hidden flex h-6 w-6 items-center justify-center rounded-full bg-red-400 text-white group-hover:flex"
              >
                −
              </button>

              <input
                type="checkbox"
                :checked="item.checked"
                class="h-5 w-5"
                @change="toggleItem(index)"
              />
            </div>
          </template>

          <!-- Edit mode -->
          <template v-else>
            <input
              v-model="editingText"
              class="flex-1 rounded-xl border bg-white p-2 text-sm outline-none focus:outline-none focus:ring-0 focus:shadow-none focus:border-[#94A3B8]"
              @keyup.enter="saveEdit"
              @keyup.esc="cancelEdit"
            />

            <div class="ml-2 flex gap-2">
              <button
                type="button"
                @click="saveEdit"
                class="rounded-xl bg-[#94A3B8] px-3 py-2 text-xs text-white"
              >
                儲存
              </button>

              <button
                type="button"
                @click="cancelEdit"
                class="rounded-xl bg-gray-200 px-3 py-2 text-xs text-gray-600"
              >
                取消
              </button>
            </div>
          </template>
        </div>

        <p
          v-if="localItems.length === 0"
          class="py-10 text-center text-sm text-gray-400"
        >
          目前沒有購物項目
        </p>
      </div>

      <!-- Fixed input -->
      <div class="mt-4 flex items-end gap-3 border-t pt-3">
        <input
          v-model="newItemName"
          type="text"
          placeholder="新增購物物品"
          :class="inputClass"
          @keyup.enter="addItem"
        />

        <button
          type="button"
          @click="addItem"
          class="flex h-9 w-9 flex-shrink-0 items-center justify-center rounded-full bg-[#94A3B8] text-lg text-white shadow-sm hover:opacity-90"
        >
          +
        </button>
      </div>
    </div>
  </div>
</template>