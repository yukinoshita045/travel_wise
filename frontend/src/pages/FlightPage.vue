<script setup>
import { ref, computed } from "vue";
import {
  Clock,
  TicketsPlane,
  Bed,
  Plane,
  CircleArrowLeft,
  CircleArrowRight
} from "lucide-vue-next";

const flights = [
  {
    flightNumber: "CI100",
    airline: "China Airlines",
    departure: {
      city: "Taipei",
      country: "Taiwan",
      timezone: "Asia/Taipei",
      time: "08:00",
    },
    arrival: {
      city: "Tokyo",
      country: "Japan",
      timezone: "Asia/Tokyo",
      time: "11:30",
    },
    flightDurationHours: 3.5,
  },
  {
    flightNumber: "BR198",
    airline: "EVA Air",
    departure: {
      city: "Taipei",
      country: "Taiwan",
      timezone: "Asia/Taipei",
      time: "15:10",
    },
    arrival: {
      city: "Seoul",
      country: "South Korea",
      timezone: "Asia/Seoul",
      time: "18:40",
    },
    flightDurationHours: 2.5,
  },
];

const index = ref(0);

const flightData = computed(() => flights[index.value]);

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
  index.value = (index.value + 1) % flights.length;
};

const prevFlight = () => {
  index.value =
    (index.value - 1 + flights.length) % flights.length;
};


const goBack = () => {
  window.history.back();
};
</script>

<template>
  <div class="h-screen bg-[#F8FAFC] px-6 py-6 flex flex-col">

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
    <div class="flex flex-1 items-center justify-center gap-20 -translate-y-6">

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
                82%
              </p>
            </div>

            <div class="h-3 overflow-hidden rounded-full bg-gray-200">
              <div class="h-full w-[82%] bg-[#7E99BF]" />
            </div>

            <p class="mt-3 text-sm text-gray-500">
              建議抵達後休息 2 小時，能更好地進行後續行程。
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
  </div>
</template>