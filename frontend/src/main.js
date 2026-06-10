import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { loadTripsFromApi } from './data/travelStore'

// 啟動時若已登入（有 authToken）才從後端同步旅程資料；未登入時等登入成功後再載入
// 失敗不影響 UI，降級使用 localStorage
if (localStorage.getItem('authToken')) {
  loadTripsFromApi()
}

createApp(App).use(router).mount('#app')