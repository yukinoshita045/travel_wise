<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  Clock,
  TicketsPlane,
  Bed,
  Plane
} from "lucide-vue-next";
import Navbar from "../components/Navbar.vue";
import { getTripOrDefault, refreshFatigueForTrip } from "../data/travelStore.js";

const route = useRoute();
const router = useRouter();
const trip = computed(() => getTripOrDefault(route.params.id));
const flights = computed(() => trip.value.flights || []);

const index = ref(0);

const flightData = computed(() => flights.value[index.value] || flights.value[0]);

// ── 疲勞詳細資料（從 _fatigueDetail 取，沒有就用預設值）────────
const fatigueDetail = computed(() => trip.value._fatigueDetail || null)
const fatigueScore = computed(() => {
  if (fatigueDetail.value?.energyBattery != null) return fatigueDetail.value.energyBattery
  // fallback：把 trip.fatigue "45%" → 55（100 - 45）
  const raw = trip.value.fatigue || ''
  const num = parseFloat(raw)
  return isNaN(num) ? 82 : Math.max(0, 100 - num)
})
const fatigueExplanation = computed(() =>
  fatigueDetail.value?.explanation || '建議抵達後休息 2 小時，能更好地進行後續行程。'
)
const suggestedStartTime = computed(() =>
  fatigueDetail.value?.suggestedStartTime || '10:00'
)
const recoverHours = computed(() =>
  fatigueDetail.value?.recoverHours ?? 2
)

const formatDuration = (hours) => {
  const h = Math.floor(hours);
  const m = Math.round((hours - h) * 60);
  if (m === 0) return `${h}h`;
  return `${h}h ${m}m`;
};

const formatLocation = (location) => {
  return `${location.city}, ${location.country}`;
};

const getTimezoneLabel = (timezone) => {
  return timezone.replace("Asia/", "");
};

const sleepMode = ref(true);

const toggleSleepMode = () => {
  sleepMode.value = !sleepMode.value;
};

const nextFlight = () => {
  if (!flights.value.length) return;
  index.value = (index.value + 1) % flights.value.length;
};

const prevFlight = () => {
  if (!flights.value.length) return;
  index.value =
    (index.value - 1 + flights.value.length) % flights.value.length;
};

const goBack = () => {
  router.push(`/trip/${trip.value.id}`);
};

onMounted(() => {
  const id = route.params.id || trip.value?.id
  if (id) refreshFatigueForTrip(id)
})
</script>

<template>
  <div class="h-screen bg-[#F8FAFC] px-6 pb-6 pt-24 flex flex-col">
    <Navbar />

    <!-- Header -->
    <div class="mb-6 flex items-center justify-between">
      <h1 class="text-3xl font-bold text-[#1E293B]">
        航班資訊
      </h1>

      <button
        @click="goBack"
        class="rounded-full bg-[#94A3B8] px-4 py-2 text-sm font-medium text-white shadow"
      >
        ← 返回
      </button>
    </div>

    <!-- Main -->
    <div v-if="flightData" class="flex flex-1 items-center justify-center gap-20 -translate-y-6">

      <!-- Left Arrow -->
      <button
        @click="prevFlight"
        class="flex h-12 w-12 items-center justify-center rounded-full bg-white shadow transition hover:scale-105"
      >
        ←
      </button>

      <!-- Flight Card -->
      <div
        class="relative flex h-[450px] w-[50%] flex-col overflow-hidden rounded-3xl bg-[#7E99BF] shadow-xl"
      >

        <!-- Blue Area -->
        <div class="flex-1 p-10">

          <!-- Top -->
          <div>
            <p class="text-xs tracking-widest text-[#DBE1FF]">
              FLIGHT NUMBER
            </p>

            <h2 class="text-3xl font-bold text-white">
              {{ flightData.flightNumber }}
            </h2>

            <p class="text-sm text-[#DBE1FF]">
              {{ flightData.airline }}
            </p>
          </div>

          <!-- Route -->
          <div class="mt-10 flex items-center justify-between">

            <!-- Departure -->
            <div class="text-center">
              <p class="text-sm text-[#DBE1FF]">
                起飛
              </p>

              <p class="mt-1 w-[200px] text-xl font-semibold text-white">
                {{ formatLocation(flightData.departure) }}
              </p>

              <p class="text-lg text-white">
                {{ flightData.departure.time }}
              </p>

              <p class="text-sm text-[#DBE1FF]">
                {{ flightData.departure.timezone }}
              </p>
            </div>

            <!-- Plane -->
            <div class="flex items-center justify-center">
              <div class="rounded-full bg-white/20 p-3">
                <Plane class="h-6 w-6 rotate-45 text-white" />
              </div>
            </div>

            <!-- Arrival -->
            <div class="text-center">
              <p class="text-sm text-[#DBE1FF]">
                抵達
              </p>

              <p class="mt-1 w-[200px] text-xl font-semibold text-white">
                {{ formatLocation(flightData.arrival) }}
              </p>

              <p class="text-lg text-white">
                {{ flightData.arrival.time }}
              </p>

              <p class="text-sm text-[#DBE1FF]">
                {{ flightData.arrival.timezone }}
              </p>
            </div>

          </div>
        </div>

        <!-- Bottom White -->
        <div class="h-20 bg-white" />

      </div>

      <!-- Detail Panel -->
      <div class="w-[400px]">

        <h2 class="mb-6 text-2xl text-[#191C1E]">
          行程細節
        </h2>

        <div class="space-y-4">

          <!-- Duration -->
          <div
            class="flex items-center justify-between rounded-2xl bg-white px-5 py-4 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <Clock class="text-[#7E99BF]" />
              <p>飛行時長</p>
            </div>

            <p>{{ formatDuration(flightData.flightDurationHours) }}</p>
          </div>

          <!-- Transfer -->
          <div
            class="flex items-center justify-between rounded-2xl bg-white px-5 py-4 shadow-sm"
          >
            <div class="flex items-center gap-3">

              <TicketsPlane class="text-[#7E99BF]" />

              <p>轉機次數</p>
            </div>

            <p>
              {{
                flights.length - 1 === 0
                  ? "直飛"
                  : `${flights.length - 1} 次`
              }}
            </p>
          </div>

          <!-- Timezone -->
          <!-- <div
            class="flex items-center justify-between rounded-2xl bg-white px-5 py-4 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <Clock class="text-[#7E99BF]" />
              <p>時區</p>
            </div>

            <p class="text-sm text-gray-600">
              {{ getTimezoneLabel(flightData.departure.timezone) }}
              →
              {{ getTimezoneLabel(flightData.arrival.timezone) }}
            </p>
          </div> -->

          <!-- Sleep -->
          <div
            class="flex items-center justify-between rounded-2xl bg-white px-5 py-4 shadow-sm"
          >
            <div class="flex items-center gap-3">
              <Bed class="text-[#7E99BF]" />
              <p>補眠</p>
            </div>

            <button
              type="button"
              @click="toggleSleepMode"
              :class="[
                'relative h-7 w-12 rounded-full transition',
                sleepMode ? 'bg-[#94A3B8]' : 'bg-gray-300'
              ]"
            >
              <div
                :class="[
                  'absolute top-1 h-5 w-5 rounded-full bg-white transition',
                  sleepMode ? 'right-1' : 'left-1'
                ]"
              />
            </button>
          </div>

          <!-- Progress -->
          <div class="rounded-2xl bg-white p-5 shadow-sm">

            <div class="mb-2 flex justify-between">
              <p class="font-semibold">
                時差適應指數
              </p>

              <p class="font-bold text-[#7E99BF]">
                {{ fatigueScore }}%
              </p>
            </div>

            <div class="h-3 overflow-hidden rounded-full bg-gray-200">
              <div class="h-full bg-[#7E99BF]" :style="{ width: fatigueScore + '%' }" />
            </div>

            <p class="mt-3 text-sm text-gray-500">
              {{ fatigueExplanation }}
            </p>

            <p v-if="fatigueDetail" class="mt-1 text-xs text-[#7E99BF]">
              建議活動起始：{{ suggestedStartTime }}　｜　恢復需 {{ recoverHours }} 小時
            </p>

          </div>

        </div>
      </div>

      <!-- Right Arrow -->
      <button
        @click="nextFlight"
        class="flex h-12 w-12 items-center justify-center rounded-full bg-white shadow transition hover:scale-105"
      >
        →
      </button>

    </div>

    <div v-else class="flex flex-1 items-center justify-center rounded-3xl bg-white text-[#64748B] shadow-sm">
      尚未新增航班資訊
    </div>
  </div>
</template>
