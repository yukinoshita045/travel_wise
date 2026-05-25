import { createRouter, createWebHistory } from 'vue-router'
import TripPlan from '../pages/TripPlan.vue'
// 1. 引入你的主頁面 (因為檔案在 src 底下，所以用 ../ 回到上一層)
import TravelDashboard from '../TravelDashboard.vue' 

const router = createRouter({
  history: createWebHistory(),
  routes: [
    // 2. 將首頁路徑 (/) 直接綁定給你的儀表板元件
    { path: '/', component: TravelDashboard },
    
    // 保留組員原本寫的行程頁面路由，完全不影響他的進度
    { path: '/trip/:id/plan', component: TripPlan },
  ]
})

export default router