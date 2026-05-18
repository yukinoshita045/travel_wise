import { createRouter, createWebHistory } from 'vue-router'
import TripPlan from '../pages/TripPlan.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/trip/1/plan' },
    { path: '/trip/:id/plan', component: TripPlan },
  ],
})

export default router