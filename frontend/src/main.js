import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import { loadTripsFromApi } from './data/travelStore'

// 啟動時嘗試從後端同步旅程資料（失敗不影響 UI，降級使用 localStorage）
loadTripsFromApi()

createApp(App).use(router).mount('#app')