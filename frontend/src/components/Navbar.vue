<template>
    <nav class="fixed left-0 right-0 top-0 z-40 flex w-screen items-center justify-between bg-white/80 px-6 py-3 shadow-sm backdrop-blur-md">
        <div class="flex items-center gap-2 text-[#2B55CC] font-bold text-xl tracking-wider">
            <svg class="w-9 h-9" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="256" cy="256" r="230" stroke="currentColor" stroke-width="12" />
                <ellipse cx="256" cy="160" rx="125" ry="75" stroke="currentColor" stroke-width="12" />
                <polyline points="136,180 220,180 240,100 256,275 268,160 278,180 376,180" stroke="currentColor" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>
                <g transform="translate(325, 150) scale(0.7) rotate(60)">
                    <path d="M -2,-15 Q 0,-20 2,-15 L 3,-2 L 20,4 L 20,8 L 3,5 L 2,12 L 8,16 L 8,18 L 0,16 L -8,18 L -8,16 L -2,12 L -3,5 L -20,8 L -20,4 L -3,-2 Z" fill="currentColor" />
                </g>
                <path d="M 161 250 L 351 250 C 351 350, 300 430, 256 455 C 212 430, 161 350, 161 250 Z" stroke="currentColor" stroke-width="12" stroke-linejoin="round" stroke-linecap="round" />
            </svg>
            TravelWise
        </div>
        <div class="relative">
          <div 
            @click="showProfileMenu = !showProfileMenu" 
            class="flex items-center gap-3 cursor-pointer group"
          >
            <div class="w-10 h-10 rounded-full bg-slate-50 flex items-center justify-center border border-slate-200 shadow-sm text-slate-400 group-hover:bg-blue-50 group-hover:text-[#2B55CC] group-hover:border-blue-100 transition-colors">
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            </div>
            <span class="text-sm text-slate-700 font-bold hidden sm:block group-hover:text-[#2B55CC] transition-colors">個人檔案</span>
          </div>

          <div v-show="showProfileMenu" class="absolute right-0 mt-3 w-48 bg-white rounded-xl shadow-[0_5px_15px_-3px_rgba(0,0,0,0.1)] border border-slate-100 py-1 z-50">
            <div class="px-4 py-3 border-b border-slate-50">
              <p class="text-sm font-bold text-slate-700">TravelWise 旅客</p>
              <p class="text-xs text-slate-400 truncate mt-0.5">user@travelwise.com</p>
            </div>
            <a href="#" @click.prevent="handleSettingsClick" class="block px-4 py-2 text-sm text-slate-600 hover:bg-slate-50 hover:text-[#2B55CC] transition-colors">
              個人設定
            </a>
            <button @click="handleLogout" class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors">
              登出系統
            </button>
          </div>
        </div>
    </nav>
</template>

<script setup>
import { ref } from 'vue';

const showProfileMenu = ref(false);

const handleSettingsClick = () => {
  alert('個人設定功能開發中，敬請期待！');
};

const handleLogout = () => {
  sessionStorage.removeItem('travelwise:currentUser');
  window.location.href = '/';
};
</script>
