import { createRouter, createWebHistory } from 'vue-router'
import TripPlan from '../pages/TripPlan.vue'
import TravelDashboard from '../TravelDashboard.vue'
import TripOverviewPage from '../pages/TripOverviewPage.vue'
import ItineraryPage from '../pages/ItineraryPage.vue'
import FlightPage from '../pages/FlightPage.vue'
import ItemPage from '../pages/ItemPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: TravelDashboard },
    { path: '/trip/:id', component: TripOverviewPage },
    { path: '/trip/:id/itinerary', component: ItineraryPage },
    { path: '/trip/:id/flights', component: FlightPage },
    { path: '/trip/:id/items', component: ItemPage },
    { path: '/trip/:id/plan', component: TripPlan },
  ]
})

export default router
