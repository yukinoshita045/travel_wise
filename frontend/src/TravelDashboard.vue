<template>
  <div>
      <Auth v-if="!isLoggedIn" @login-success="handleLogin" />

      <div v-else class="min-h-screen pb-20">
      <!-- 頂部導覽列 -->
       <Navbar />
      <!-- 主視圖區塊 -->
      <main class="max-w-6xl mx-auto px-4 sm:px-6 pt-24">
          <!-- Hero Banner -->
          <div class="relative w-full h-48 md:h-64 rounded-[30px] overflow-hidden shadow-md mb-8 group">
              <img :src="coverPhotoUrl" alt="封面照片" class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105">
              <div class="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent transition-opacity duration-300 group-hover:opacity-80"></div>
              
              <button @click="triggerFileInput" :disabled="isCompressing" class="absolute bottom-5 right-5 bg-white/20 hover:bg-white/40 backdrop-blur-md text-white px-4 py-2.5 rounded-xl flex items-center gap-2 transition-all duration-300 opacity-0 group-hover:opacity-100 border border-white/30 shadow-lg disabled:opacity-80 disabled:cursor-wait">
                  <svg v-if="isCompressing" class="animate-spin w-5 h-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                  <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                  <span class="text-sm font-bold tracking-wider">{{ isCompressing ? '處理中...' : '更換封面' }}</span>
              </button>
              <input type="file" ref="fileInput" @change="handlePhotoUpload" accept="image/*" class="hidden">
          </div>

          <!-- 操作區塊 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-10">
              <button @click="openModal" class="flex items-center px-6 py-5 rounded-3xl bg-white border border-slate-200 shadow-[0_2px_8px_-2px_rgba(0,0,0,0.05)] hover:border-[#2B55CC]/40 hover:shadow-[0_4px_12px_-2px_rgba(43,85,204,0.12)] transition-all duration-300 w-full">
                  <div class="mr-4 text-[#2B55CC]">
                      <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 9v4m-2-2h4"></path></svg>
                  </div>
                  <div class="text-left">
                      <h3 class="text-xl font-bold text-slate-700 tracking-wider mb-1">按此新增行程</h3>
                      <p class="text-slate-500 text-xs font-medium">趕快來與TravelWise一起規劃下次旅行吧！</p>
                  </div>
              </button>

              <div class="relative w-full h-full">
                  <button v-if="!isSearching" @click="startSearch" class="flex items-center px-6 py-5 rounded-3xl bg-white border border-slate-300 hover:border-slate-400 hover:bg-slate-50 transition-all duration-300 w-full h-full">
                      <div class="mr-4 text-slate-500">
                          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                      </div>
                      <div class="text-left">
                          <h3 class="text-xl font-bold text-slate-700 tracking-wider">搜尋過去行程規劃</h3>
                      </div>
                  </button>
                  <div v-else class="flex items-center px-6 py-5 rounded-3xl bg-white border border-[#2B55CC] shadow-[0_4px_12px_-2px_rgba(43,85,204,0.12)] transition-all duration-300 w-full h-full">
                      <div class="mr-4 text-[#2B55CC]">
                          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                      </div>
                      <input type="text" v-model="searchQuery" ref="searchInput" @blur="handleSearchBlur" placeholder="輸入目的地或日期..." class="w-full bg-transparent text-xl font-bold text-slate-700 placeholder-slate-400 outline-none">
                      <button @click="clearSearch" v-show="searchQuery" class="ml-2 text-slate-400 hover:text-slate-600">
                          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                      </button>
                  </div>
              </div>
          </div>

          <!-- 行程卡片列表 -->
          <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <TripCard 
                v-for="trip in filteredTrips" 
                :key="trip.id" 
                :trip="trip" 
                @edit="openEditModal" 
                @open="openTrip"
              />

              <div v-if="filteredTrips.length === 0" class="col-span-full py-10 text-center text-slate-500">
                  <p>找不到符合條件的行程。</p>
              </div>
          </div>
      </main>

      <TripModal 
        v-if="isModalOpen" 
        :trip-data="editingTrip"
        :is-submitting="isSubmitting"
        @close="closeModal"
        @submit="handleSaveTrip"
      />
      </div>
  </div>
</template>

<script setup>
import myCoverImage from './assets/IMG_5224.JPG';
import { ref, computed, watch, nextTick } from 'vue';
import { useRouter } from 'vue-router';
import { compressImage } from './utils/imageUtils.js';
import Navbar from './components/Navbar.vue';
import TripCard from './components/TripCard.vue';
import TripModal from './components/TripModal.vue'; // 👈 引入彈窗元件
import Auth from './components/Auth.vue'; // 👈 引入登入元件
import { addTrip, trips, updateTrip } from './data/travelStore.js';

const router = useRouter();
const savedUser = sessionStorage.getItem('travelwise:currentUser') || '';

// 預設為 false (未登入狀態)
const isLoggedIn = ref(Boolean(savedUser)); 
const currentUser = ref(savedUser);

// 當 Auth 元件發送 login-success 事件時觸發
const handleLogin = (username) => {
    currentUser.value = username;
    isLoggedIn.value = true;
    sessionStorage.setItem('travelwise:currentUser', username);
};

const defaultCover = myCoverImage;
const coverPhotoUrl = ref(localStorage.getItem('savedCoverPhoto') || defaultCover);
const fileInput = ref(null);
const isCompressing = ref(false);

const triggerFileInput = () => { if (fileInput.value) fileInput.value.click(); };

const handlePhotoUpload = async (event) => {
  const file = event.target.files[0];
  if (file) {
      try {
          isCompressing.value = true;
          if (coverPhotoUrl.value && coverPhotoUrl.value.startsWith('blob:')) URL.revokeObjectURL(coverPhotoUrl.value);
          const compressedBlob = await compressImage(file, 1920, 1080, 0.8);
          coverPhotoUrl.value = URL.createObjectURL(compressedBlob);
      } catch (error) {
          console.error("圖片壓縮失敗:", error);
      } finally {
          isCompressing.value = false;
          if (fileInput.value) fileInput.value.value = '';
      }
  }
};

// --- 以下是精簡過後的彈窗管理邏輯 ---
const isModalOpen = ref(false);
const isSubmitting = ref(false);
const editingTrip = ref(null); // 改成儲存整筆行程物件

const openModal = () => {
  editingTrip.value = null; // 新增模式
  isModalOpen.value = true;
};

const openEditModal = (trip) => {
  editingTrip.value = trip; // 編輯模式
  isModalOpen.value = true;
};

const openTrip = (trip) => {
  router.push(`/trip/${trip.id}`);
};

const closeModal = () => { 
  if (!isSubmitting.value) isModalOpen.value = false; 
};

// 當 TripModal 驗證完畢發送 submit 事件時，就會觸發這裡儲存資料
const handleSaveTrip = (formData) => {
  isSubmitting.value = true;
  
  setTimeout(() => {
      if (editingTrip.value) {
          updateTrip(editingTrip.value.id, formData);
      } else {
          addTrip(formData);
      }
      isSubmitting.value = false;
      closeModal();
  }, 800);
};

// --- 搜尋邏輯維持不變 ---
const isSearching = ref(false);
const searchQuery = ref('');
const debouncedSearchQuery = ref('');
const searchInput = ref(null);
let searchTimeout = null;

watch(searchQuery, (newVal) => {
  if (searchTimeout) clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => { debouncedSearchQuery.value = newVal; }, 300);
});

const startSearch = async () => { isSearching.value = true; await nextTick(); if (searchInput.value) searchInput.value.focus(); };
const clearSearch = () => { searchQuery.value = ''; };
const handleSearchBlur = () => { if (!searchQuery.value) isSearching.value = false; };

const filteredTrips = computed(() => {
  if (!debouncedSearchQuery.value) return trips;
  const q = debouncedSearchQuery.value.toLowerCase();
  return trips.filter(t => t.title.toLowerCase().includes(q) || t.date.toLowerCase().includes(q) || t.dates.toLowerCase().includes(q));
});
</script>

<style>
.modal-enter-active, .modal-leave-active { transition: all 0.3s ease; }
.modal-enter-from, .modal-leave-to { opacity: 0; transform: scale(0.95); }
.toggle-checkbox:checked { right: 0; border-color: #2B55CC; }
.toggle-checkbox:checked + .toggle-label { background-color: #2B55CC; }
</style>
