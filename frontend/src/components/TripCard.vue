<template>
    <div class="bg-white rounded-3xl p-6 shadow-[0_2px_10px_-3px_rgba(6,81,237,0.1)] border border-slate-50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 relative cursor-pointer group">
        <div v-if="trip.isUpcoming" class="absolute top-5 right-14">
            <span class="flex items-center gap-1.5 px-3 py-1 bg-red-50 text-red-600 text-xs font-bold tracking-wider rounded-full border border-red-100">
                <span class="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse"></span> 即將到來！
            </span>
        </div>
        <div @click.stop="$emit('edit', trip)" class="absolute top-5 right-4 w-8 h-8 rounded-full flex items-center justify-center text-slate-300 hover:text-slate-600 hover:bg-slate-100 transition-colors z-10 cursor-pointer">
            <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M6 12a2 2 0 11-4 0 2 2 0 014 0zM14 12a2 2 0 11-4 0 2 2 0 014 0zM22 12a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
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
            </div>
            <div class="pt-3 mt-2 border-t border-slate-50 flex items-center justify-between">
                <span class="text-slate-400">預算</span>
                <span class="font-bold text-sm text-slate-800">________({{ trip.budget }})</span>
            </div>
        </div>
    </div>
</template>

<script setup>
// 定義這個元件需要接收哪些資料 (Props)
defineProps({
    trip: {
        type: Object,
        required: true
    }
});

// 定義這個元件可以向外發送哪些事件 (Emits)
defineEmits(['edit']);
</script>