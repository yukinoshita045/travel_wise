<template>
  <transition name="modal">
      <div class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4">
          <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg overflow-hidden flex flex-col" @click.stop>
              <div class="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50">
                  <h3 class="text-xl font-bold text-slate-800 tracking-wider flex items-center gap-2">
                      <span class="w-2 h-6 bg-[#2B55CC] rounded-full inline-block"></span>
                      {{ tripData ? '編輯行程' : (modalStep === 1 ? '新增行程 - 基本資訊' : '新增行程 - 轉機設定') }}
                  </h3>
                  <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 transition-colors p-1">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
              </div>
              <div class="p-6">
                  <div v-show="modalStep === 1" class="space-y-5">
                      <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1">目的地 <span class="text-red-500">*</span></label>
                          <div class="relative">
                              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg></div>
                              <input type="text" v-model="form.destination" placeholder="例如：日本 東京" :class="{'border-red-400 focus:ring-red-400/50': errors.destination}" class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2B55CC]/50 focus:border-[#2B55CC] outline-none transition-all">
                          </div>
                          <p v-if="errors.destination" class="text-xs text-red-500 mt-1">{{ errors.destination }}</p>
                      </div>
                      <div class="grid grid-cols-2 gap-4">
                          <div>
                              <label class="block text-sm font-medium text-slate-600 mb-1">出發日期 <span class="text-red-500">*</span></label>
                              <div class="relative">
                                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>
                                  <input type="date" v-model="form.startDate" :class="{'border-red-400 focus:ring-red-400/50': errors.dates}" class="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2B55CC]/50 focus:border-[#2B55CC] outline-none transition-all">
                              </div>
                          </div>
                          <div>
                              <label class="block text-sm font-medium text-slate-600 mb-1">回程日期 <span class="text-red-500">*</span></label>
                              <div class="relative">
                                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg></div>
                                  <input type="date" v-model="form.endDate" :class="{'border-red-400 focus:ring-red-400/50': errors.dates}" class="w-full pl-9 pr-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2B55CC]/50 focus:border-[#2B55CC] outline-none transition-all">
                              </div>
                          </div>
                          <p v-if="errors.dates" class="text-xs text-red-500 col-span-2">{{ errors.dates }}</p>
                      </div>
                      <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1">同行者帳號 (選填)</label>
                          <div class="relative">
                              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg></div>
                              <input type="text" v-model="form.companion" placeholder="例如：@user123, @travelmate" class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2B55CC]/50 focus:border-[#2B55CC] outline-none transition-all">
                          </div>
                      </div>
                      <div class="flex items-center justify-between p-4 bg-slate-50 rounded-lg border border-slate-100 mt-2">
                          <div>
                              <p class="font-bold text-slate-700">是否需要轉機？</p>
                              <p class="text-xs text-slate-500">若勾選，將進入下一步設定轉機機場</p>
                          </div>
                          <div class="relative inline-block w-12 mr-2 align-middle select-none transition duration-200 ease-in">
                              <input type="checkbox" v-model="form.needLayover" id="toggle" class="toggle-checkbox absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer transition-all duration-300 z-10 top-0 left-0"/>
                              <label for="toggle" class="toggle-label block overflow-hidden h-6 rounded-full bg-slate-300 cursor-pointer transition-colors duration-300"></label>
                          </div>
                      </div>
                  </div>
                  <div v-show="modalStep === 2" class="space-y-5">
                      <div class="bg-blue-50 border border-blue-100 p-4 rounded-lg flex gap-3 text-blue-800 text-sm mb-4">
                          <svg class="w-5 h-5 shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                          <p>請設定您的轉機資訊，這將幫助 TravelWise 更準確計算您的「疲勞指數」。</p>
                      </div>
                      <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1">轉機機場 / 城市</label>
                          <div class="relative">
                              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></div>
                              <input type="text" v-model="form.layoverCity" placeholder="例如：香港 HKG" class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2B55CC]/50 focus:border-[#2B55CC] outline-none transition-all">
                          </div>
                      </div>
                      <div>
                          <label class="block text-sm font-medium text-slate-600 mb-1">預計轉機停留時間 (小時)</label>
                          <div class="relative">
                              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400"><svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg></div>
                              <input type="number" v-model="form.layoverHours" placeholder="例如：4" min="0" class="w-full pl-10 pr-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-[#2B55CC]/50 focus:border-[#2B55CC] outline-none transition-all">
                          </div>
                      </div>
                  </div>
              </div>
              <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
                  <button v-if="modalStep === 1" @click="$emit('close')" :disabled="isSubmitting" class="px-5 py-2 rounded-lg font-bold text-slate-500 hover:bg-slate-200 transition-colors disabled:opacity-50">取消</button>
                  <button v-if="modalStep === 2" @click="modalStep = 1" :disabled="isSubmitting" class="px-5 py-2 rounded-lg font-bold text-slate-500 hover:bg-slate-200 transition-colors disabled:opacity-50">上一步</button>
                  <button @click="handleSubmit" :disabled="isSubmitting" class="px-6 py-2 rounded-lg font-bold text-white bg-[#2B55CC] hover:bg-[#1f42a6] shadow-md hover:shadow-lg transform hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:transform-none flex items-center gap-2">
                      <svg v-if="isSubmitting" class="animate-spin h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                      {{ isSubmitting ? '處理中...' : primaryButtonText }}
                  </button>
              </div>
          </div>
      </div>
  </transition>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';

// 接收來自 App.vue 的資料 (用來判斷是新增還是編輯，以及載入中狀態)
const props = defineProps({
  tripData: { type: Object, default: null },
  isSubmitting: { type: Boolean, default: false }
});

// 定義可以回傳給 App.vue 的事件
const emit = defineEmits(['close', 'submit']);

const modalStep = ref(1);

// 表單狀態
const form = reactive({
  destination: props.tripData ? props.tripData.title : '',
  startDate: '',
  endDate: '',
  needLayover: false,
  layoverCity: '',
  layoverHours: '',
  companion: props.tripData && props.tripData.users !== '僅自己' ? props.tripData.users : ''
});

const errors = reactive({ destination: '', dates: '' });

const primaryButtonText = computed(() => {
  if (modalStep.value === 1 && form.needLayover) return '下一步';
  return props.tripData ? '儲存變更' : '確認新增';
});

// 表單驗證邏輯
const validateForm = () => {
  let isValid = true; errors.destination = ''; errors.dates = '';
  if (!form.destination.trim()) { errors.destination = '請填寫目的地'; isValid = false; }
  if (!form.startDate || !form.endDate) { errors.dates = '請完整填寫出發與回程日期'; isValid = false; }
  else {
      if (new Date(form.endDate) < new Date(form.startDate)) { errors.dates = '回程日期不能早於出發日期'; isValid = false; }
  }
  return isValid;
};

// 按下確認鈕
const handleSubmit = () => {
  if (!validateForm()) return;
  if (modalStep.value === 1 && form.needLayover) {
      modalStep.value = 2;
  } else {
      // 驗證成功後，把整包表單資料「往外丟」給 App.vue 去處理儲存
      emit('submit', form);
  }
};
</script>