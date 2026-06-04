<template>
    <div @click="$emit('open', trip)" class="bg-white rounded-3xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-slate-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 relative cursor-pointer group">
        <div v-if="trip.isUpcoming" class="absolute top-5 right-14">
            <span class="flex items-center gap-1.5 px-3 py-1 bg-red-50 text-red-600 text-xs font-bold tracking-wider rounded-full border border-red-100">
                <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> 即將到來！
            </span>
        </div>
        <button
            type="button"
            @click.stop="toggleMenu"
            class="absolute top-5 right-4 z-20 flex h-8 w-8 items-center justify-center rounded-full text-slate-300 transition-colors hover:bg-slate-100 hover:text-slate-600"
            aria-label="行程操作"
        >
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 12a2 2 0 11-4 0 2 2 0 014 0zM14 12a2 2 0 11-4 0 2 2 0 014 0zM22 12a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
        </button>
        <div
            v-if="isMenuOpen"
            @click.stop
            class="absolute right-4 top-14 z-30 w-28 overflow-hidden rounded-xl border border-slate-100 bg-white py-1 text-sm font-medium shadow-lg"
        >
            <button
                type="button"
                @click="handleEdit"
                class="block w-full px-4 py-2 text-left text-slate-700 transition-colors hover:bg-slate-50"
            >
                編輯
            </button>
            <button
                type="button"
                @click="handleDelete"
                class="block w-full px-4 py-2 text-left text-red-600 transition-colors hover:bg-red-50"
            >
                刪除
            </button>
        </div>
        <div class="flex items-center mb-5 mt-1">
            <div class="w-9 h-9 rounded-full bg-[#64748B] text-white flex items-center justify-center">
                <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M21 16v-2l-8-5V3.5c0-.83-.67-1.5-1.5-1.5S10 2.67 10 3.5V9l-8 5v2l8-2.5V19l-2 1.5V22l3.5-1 3.5 1v-1.5L13 19v-5.5l8 2.5z"></path></svg>
            </div>
        </div>
        <div class="mb-4">
            <h4 class="text-[17px] font-bold text-slate-800">{{ trip.date }} <span class="ml-1">{{ trip.title }}</span></h4>
            <p class="text-xs text-slate-500 mt-1">與 <span class="text-slate-500">{{ trip.users }}</span> 共享</p>
        </div>
        <div class="space-y-3 text-xs text-slate-600 font-medium">
            <p class="text-slate-500">{{ trip.dates }}</p>
            <div class="flex flex-wrap gap-2">
                <span class="px-2.5 py-1 bg-slate-50 border border-slate-100 rounded-md">疲勞指數：{{ trip.fatigue }}</span>
                <span class="px-2.5 py-1 bg-slate-50 border border-slate-100 rounded-md">天氣：{{ trip.weather }}</span>

                <span v-if="trip.transfers !== undefined" class="px-2.5 py-1 bg-slate-50 border border-slate-100 rounded-md">
                    {{ trip.transfers === 0 ? '直飛' : `轉機 ${trip.transfers} 次` }}
                </span>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';

// 定義這個元件需要接收哪些資料 (Props)
const props = defineProps({
    trip: {
        type: Object,
        required: true
    }
});

// 定義這個元件可以向外發送哪些事件 (Emits)
const emit = defineEmits(['edit', 'delete', 'open']);

const isMenuOpen = ref(false);

const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
};

const handleEdit = () => {
    isMenuOpen.value = false;
    emit('edit', props.trip);
};

const handleDelete = () => {
    isMenuOpen.value = false;
    emit('delete', props.trip);
};
</script>
