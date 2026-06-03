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
import {
  getTripOrDefault,
  refreshFatigueForTrip,
  addFlightToTrip,
  removeFlightFromTrip,
} from "../data/travelStore.js";
import { fetchFlightInfo } from "../api/flight.js";

const route = useRoute();
const router = useRouter();
const trip = computed(() => getTripOrDefault(route.params.id));
const flights = computed(() => trip.value.flights || []);

const index = ref(0);

// ── 航班查詢 Modal ────────────────────────────────────────
const showQueryModal = ref(false);
const queryForm = ref({ flightNum: "", date: trip.value.startDate || "" });
const querying = ref(false);
const queryError = ref("");

const openQueryModal = () => {
  queryForm.value = { flightNum: "", date: trip.value.startDate || "" };
  queryError.value = "";
  showQueryModal.value = true;
};

const submitFlightQuery = async () => {
  queryError.value = "";
  const flightNum = queryForm.value.flightNum.trim();
  const date = queryForm.value.date;
  if (!flightNum || !date) {
    queryError.value = "請輸入航班編號與出發日期";
    return;
  }
  querying.value = true;
  try {
    const res = await fetchFlightInfo(flightNum, date);
    await addFlightToTrip(trip.value.id || trip.value.tripId, res.data);
    index.value = flights.value.length - 1; // 跳到新加入的航班
    showQueryModal.value = false;
  } catch (err) {
    queryError.value =
      err?.response?.data?.error || "查詢失敗，請確認航班編號與日期是否正確";
  } finally {
    querying.value = false;
  }
};

const deleteCurrentFlight = async () => {
  if (!flights.value.length) return;
  if (!window.confirm("確定要刪除這筆航班嗎？")) return;
  const removeAt = index.value;
  await removeFlightFromTrip(trip.value.id || trip.value.tripId, removeAt);
  index.value = Math.max(0, Math.min(index.value, flights.value.length - 1));
};

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

      <div class="flex items-center gap-3">
        <button
          @click="openQueryModal"
          class="rounded-full bg-[#7E99BF] px-4 py-2 text-sm font-medium text-white shadow transition hover:opacity-90"
        >
          ＋ 新增 / 查詢航班
        </button>
        <button
          @click="goBack"
          class="rounded-full bg-[#94A3B8] px-4 py-2 text-sm font-medium text-white shadow"
        >
          ← 返回
        </button>
      </div>
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

        <!-- 刪除目前航班 -->
        <button
          @click="deleteCurrentFlight"
          class="absolute right-4 top-4 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white/20 text-white transition hover:bg-white/30"
          title="刪除此航班"
        >
          🗑
        </button>

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

    <div v-else class="flex flex-1 flex-col items-center justify-center gap-4 rounded-3xl bg-white text-[#64748B] shadow-sm">
      <p>尚未新增航班資訊</p>
      <button
        @click="openQueryModal"
        class="rounded-full bg-[#7E99BF] px-5 py-2 text-sm font-medium text-white shadow transition hover:opacity-90"
      >
        ＋ 立即查詢航班
      </button>
    </div>

    <!-- 航班查詢 Modal -->
    <div
      v-if="showQueryModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm"
      @click.self="showQueryModal = false"
    >
      <div class="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
          <h3 class="flex items-center gap-2 text-xl font-bold text-slate-800">
            <span class="inline-block h-6 w-2 rounded-full bg-[#7E99BF]"></span>
            查詢航班
          </h3>
          <button @click="showQueryModal = false" class="p-1 text-slate-400 hover:text-slate-700">✕</button>
        </div>

        <div class="space-y-4 p-6">
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-600">航班編號 <span class="text-red-500">*</span></label>
            <input
              v-model="queryForm.flightNum"
              type="text"
              placeholder="例如：BR189、CI100、IT203"
              class="w-full rounded-lg border border-slate-300 px-4 py-2 uppercase outline-none transition-all focus:border-[#7E99BF] focus:ring-2 focus:ring-[#7E99BF]/40"
              @keyup.enter="submitFlightQuery"
            />
          </div>
          <div>
            <label class="mb-1 block text-sm font-medium text-slate-600">出發日期 <span class="text-red-500">*</span></label>
            <input
              v-model="queryForm.date"
              type="date"
              class="w-full rounded-lg border border-slate-300 px-4 py-2 outline-none transition-all focus:border-[#7E99BF] focus:ring-2 focus:ring-[#7E99BF]/40"
            />
          </div>
          <p v-if="queryError" class="text-sm text-red-500">{{ queryError }}</p>
          <p class="text-xs text-slate-400">資料來源：AeroDataBox（即時班表，需該日期有排程）</p>
        </div>

        <div class="flex justify-end gap-3 border-t border-slate-100 bg-slate-50 px-6 py-4">
          <button
            @click="showQueryModal = false"
            :disabled="querying"
            class="rounded-lg px-5 py-2 font-bold text-slate-500 transition-colors hover:bg-slate-200 disabled:opacity-50"
          >
            取消
          </button>
          <button
            @click="submitFlightQuery"
            :disabled="querying"
            class="flex items-center gap-2 rounded-lg bg-[#7E99BF] px-6 py-2 font-bold text-white shadow-md transition-all hover:opacity-90 disabled:opacity-70"
          >
            <svg v-if="querying" class="h-4 w-4 animate-spin text-white" viewBox="0 0 24 24" fill="none">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            {{ querying ? '查詢中...' : '查詢並加入' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
