<template>
  <div class="bg-slate-50 min-h-screen flex items-center justify-center font-sans fixed inset-0 z-50">
      <div class="w-full max-w-md p-4">
          <div class="bg-white rounded-2xl shadow-xl overflow-hidden transition-all duration-300 pt-6">
              
              <div class="px-8 pt-4 pb-2 flex flex-col items-center justify-center">
                  <svg class="w-28 h-28" viewBox="0 0 512 512" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="256" cy="256" r="230" stroke="#2B55CC" stroke-width="12" />
                      <ellipse cx="256" cy="160" rx="125" ry="75" stroke="#2B55CC" stroke-width="12" />
                      <polyline points="136,180 220,180 240,100 256,275 268,160 278,180 376,180" stroke="#2B55CC" stroke-width="12" stroke-linejoin="round" stroke-linecap="round"/>
                      <g transform="translate(325, 150) scale(0.7) rotate(60)">
                          <path d="M -2,-15 Q 0,-20 2,-15 L 3,-2 L 20,4 L 20,8 L 3,5 L 2,12 L 8,16 L 8,18 L 0,16 L -8,18 L -8,16 L -2,12 L -3,5 L -20,8 L -20,4 L -3,-2 Z" fill="#2B55CC" />
                      </g>
                      <path d="M 161 250 L 351 250 C 351 350, 300 430, 256 455 C 212 430, 161 350, 161 250 Z" stroke="#2B55CC" stroke-width="12" stroke-linejoin="round" stroke-linecap="round" />
                  </svg>
                  <div class="text-center mt-4">
                      <h1 class="text-2xl font-bold text-slate-800 tracking-wider">TravelWise</h1>
                      <p class="text-sm text-slate-500 mt-1">全齡化旅行適應決策支援平台</p>
                  </div>
              </div>

              <div class="px-10 pb-10 pt-4">
                  <div class="text-center mb-6 h-8">
                      <h2 class="text-xl font-bold text-[#8fa4c3] tracking-wider relative inline-block">
                          <span class="bg-white px-2">{{ isLogin ? '會員登入' : '註冊新帳號' }}</span>
                          <span class="absolute bottom-0 left-0 w-full h-[2px] bg-[#8fa4c3] -z-10 translate-y-2"></span>
                      </h2>
                  </div>

                  <form @submit.prevent="handleSubmit" class="space-y-5">
                      <div class="flex items-center">
                          <label class="w-24 text-slate-500 font-medium text-lg tracking-widest shrink-0">帳號</label>
                          <input type="text" v-model="form.username" placeholder="用戶名/電子郵件" required class="w-full px-4 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#8fa4c3] focus:border-transparent transition-colors placeholder:text-slate-300">
                      </div>

                      <div class="flex items-center">
                          <label class="w-24 text-slate-500 font-medium text-lg tracking-widest shrink-0">密碼</label>
                          <input type="password" v-model="form.password" required class="w-full px-4 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#8fa4c3] focus:border-transparent transition-colors">
                      </div>

                      <transition name="fade">
                          <div v-if="!isLogin" class="flex items-center">
                              <label class="w-24 text-slate-500 font-medium text-base tracking-widest shrink-0">確認密碼</label>
                              <input type="password" v-model="form.confirmPassword" :required="!isLogin" class="w-full px-4 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#8fa4c3] focus:border-transparent transition-colors">
                          </div>
                      </transition>

                      <div class="flex gap-4 pt-4 mt-2">
                          <template v-if="isLogin">
                              <button type="button" @click="toggleMode" class="flex-1 py-2 px-4 bg-white border-2 border-[#8fa4c3] text-[#8fa4c3] font-medium text-lg rounded-[20px] hover:bg-slate-50 transition-colors tracking-widest shadow-sm">註冊</button>
                              <button type="submit" class="flex-1 py-2 px-4 bg-[#8fa4c3] border-2 border-[#8fa4c3] text-white font-medium text-lg rounded-[20px] hover:bg-[#7a8fae] transition-colors tracking-widest shadow-sm">登入</button>
                          </template>
                          <template v-else>
                              <button type="button" @click="toggleMode" class="flex-1 py-2 px-4 bg-white border-2 border-[#8fa4c3] text-[#8fa4c3] font-medium text-lg rounded-[20px] hover:bg-slate-50 transition-colors tracking-widest shadow-sm">取消</button>
                              <button type="submit" class="flex-1 py-2 px-4 bg-[#8fa4c3] border-2 border-[#8fa4c3] text-white font-medium text-lg rounded-[20px] hover:bg-[#7a8fae] transition-colors tracking-widest shadow-sm">註冊</button>
                          </template>
                      </div>
                  </form>
              </div>
          </div>
      </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';

// 定義發送給父元件的事件
const emit = defineEmits(['login-success']);

const isLogin = ref(true);
const form = reactive({ username: '', password: '', confirmPassword: '' });

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  form.username = ''; form.password = ''; form.confirmPassword = '';
};

const handleSubmit = () => {
  if (isLogin.value) {
      // 這裡未來可以串接真實後端 API 檢查帳密
      console.log('送出登入:', form.username);
      alert(`歡迎回來，${form.username}！`);
      
      // 登入成功！告訴 App.vue 可以切換畫面了
      emit('login-success', form.username);
  } else {
      if (form.password !== form.confirmPassword) {
          alert('兩次輸入的密碼不一致，請重新檢查！');
          return;
      }
      console.log('送出註冊:', form.username);
      alert('註冊成功！將為您自動登入。');
      emit('login-success', form.username);
  }
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }
input[type="password"]::-ms-reveal, input[type="password"]::-ms-clear { display: none; }
</style>