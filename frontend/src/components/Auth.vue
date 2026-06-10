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
                          <input type="email" v-model="form.username" placeholder="電子郵件" required class="w-full px-4 py-2 border border-slate-300 rounded focus:outline-none focus:ring-2 focus:ring-[#8fa4c3] focus:border-transparent transition-colors placeholder:text-slate-300">
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

                      <transition name="fade">
                          <p v-if="errorMsg" class="text-sm text-red-500 text-center -mb-2">{{ errorMsg }}</p>
                      </transition>

                      <div class="flex gap-4 pt-4 mt-2">
                          <template v-if="isLogin">
                              <button type="button" @click="toggleMode" :disabled="loading" class="flex-1 py-2 px-4 bg-white border-2 border-[#8fa4c3] text-[#8fa4c3] font-medium text-lg rounded-[20px] hover:bg-slate-50 transition-colors tracking-widest shadow-sm disabled:opacity-50">註冊</button>
                              <button type="submit" :disabled="loading" class="flex-1 py-2 px-4 bg-[#8fa4c3] border-2 border-[#8fa4c3] text-white font-medium text-lg rounded-[20px] hover:bg-[#7a8fae] transition-colors tracking-widest shadow-sm disabled:opacity-50">{{ loading ? '處理中…' : '登入' }}</button>
                          </template>
                          <template v-else>
                              <button type="button" @click="toggleMode" :disabled="loading" class="flex-1 py-2 px-4 bg-white border-2 border-[#8fa4c3] text-[#8fa4c3] font-medium text-lg rounded-[20px] hover:bg-slate-50 transition-colors tracking-widest shadow-sm disabled:opacity-50">取消</button>
                              <button type="submit" :disabled="loading" class="flex-1 py-2 px-4 bg-[#8fa4c3] border-2 border-[#8fa4c3] text-white font-medium text-lg rounded-[20px] hover:bg-[#7a8fae] transition-colors tracking-widest shadow-sm disabled:opacity-50">{{ loading ? '處理中…' : '註冊' }}</button>
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
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from 'firebase/auth';
import { auth } from '../firebase';

// 定義發送給父元件的事件
const emit = defineEmits(['login-success']);

const isLogin = ref(true);
const loading = ref(false);
const errorMsg = ref('');
const form = reactive({ username: '', password: '', confirmPassword: '' });

const toggleMode = () => {
  isLogin.value = !isLogin.value;
  errorMsg.value = '';
  form.username = ''; form.password = ''; form.confirmPassword = '';
};

// Firebase 錯誤碼轉成中文提示
const friendlyError = (code) => {
  const map = {
    'auth/invalid-email': '電子郵件格式不正確',
    'auth/user-not-found': '帳號不存在，請先註冊',
    'auth/wrong-password': '密碼錯誤',
    'auth/invalid-credential': '帳號或密碼錯誤',
    'auth/email-already-in-use': '此電子郵件已被註冊',
    'auth/weak-password': '密碼強度不足（至少 6 個字元）',
    'auth/too-many-requests': '嘗試次數過多，請稍後再試',
    'auth/network-request-failed': '網路連線失敗，請檢查網路',
  };
  return map[code] || '操作失敗，請稍後再試';
};

const handleSubmit = async () => {
  errorMsg.value = '';

  if (!isLogin.value && form.password !== form.confirmPassword) {
    errorMsg.value = '兩次輸入的密碼不一致，請重新檢查！';
    return;
  }

  loading.value = true;
  try {
    const action = isLogin.value
      ? signInWithEmailAndPassword
      : createUserWithEmailAndPassword;
    const { user } = await action(auth, form.username, form.password);

    // 取得 Firebase ID Token 供後端 require_auth 驗證
    const token = await user.getIdToken();
    localStorage.setItem('authToken', token);

    // 登入成功！告訴父元件可以切換畫面（用 email 當顯示名稱）
    emit('login-success', user.email || form.username);
  } catch (err) {
    console.error('[Auth] 認證失敗:', err?.code, err?.message);
    errorMsg.value = friendlyError(err?.code);
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: all 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }
input[type="password"]::-ms-reveal, input[type="password"]::-ms-clear { display: none; }
</style>