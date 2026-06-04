<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import {
  ChevronLeft,
  ChevronRight,
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
  saveTripChanges,
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
const editingFlightIndex = ref(null);
const flightActionMenuOpen = ref(false);

const getSegmentDate = (segment) => {
  return segment?.date || normalizeDateTime(segment?.time).date || "";
};

const openQueryModal = () => {
  editingFlightIndex.value = null;
  queryForm.value = { flightNum: "", date: trip.value.startDate || "" };
  queryError.value = "";
  showQueryModal.value = true;
};

const openEditFlightModal = () => {
  if (!flightData.value) return;

  editingFlightIndex.value = index.value;
  flightActionMenuOpen.value = false;
  queryForm.value = {
    flightNum: flightData.value.flightNumber || "",
    date: getSegmentDate(flightData.value.departure) || trip.value.startDate || "",
  };
  queryError.value = "";
  showQueryModal.value = true;
};

const closeQueryModal = () => {
  if (querying.value) return;

  showQueryModal.value = false;
  editingFlightIndex.value = null;
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
    const tripId = trip.value.id || trip.value.tripId;
    if (editingFlightIndex.value !== null) {
      trip.value.flights.splice(editingFlightIndex.value, 1, res.data);
      await saveTripChanges(tripId);
      await refreshFatigueForTrip(tripId);
      index.value = editingFlightIndex.value;
    } else {
      await addFlightToTrip(tripId, res.data);
      index.value = flights.value.length - 1; // 跳到新加入的航班
    }
    showQueryModal.value = false;
    editingFlightIndex.value = null;
  } catch (err) {
    queryError.value =
      err?.response?.data?.error || "查詢失敗，請確認航班編號與日期是否正確";
  } finally {
    querying.value = false;
  }
};

const deleteCurrentFlight = async () => {
  if (!flights.value.length) return;
  flightActionMenuOpen.value = false;
  if (!window.confirm("確定要刪除這筆航班嗎？")) return;
  const removeAt = index.value;
  await removeFlightFromTrip(trip.value.id || trip.value.tripId, removeAt);
  index.value = Math.max(0, Math.min(index.value, flights.value.length - 1));
};

const flightData = computed(() => flights.value[index.value] || flights.value[0]);
const hasMultipleFlights = computed(() => flights.value.length > 1);
const hasPreviousFlight = computed(() => index.value > 0);
const hasNextFlight = computed(() => index.value < flights.value.length - 1);

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
  if (location?.code) return location.code;
  return `${location.city}, ${location.country}`;
};

const formatLocationTitle = (location) => {
  const details = [location?.city, location?.country].filter(Boolean).join(", ");
  return location?.code && details ? `${location.code} · ${details}` : formatLocation(location);
};

const padTime = (value) => String(value).padStart(2, "0");

const normalizeDateTime = (value) => {
  if (!value) return { date: "", time: "" };

  const text = String(value).trim();
  const dateMatch = text.match(/^(\d{4}-\d{2}-\d{2})/);
  const timeMatch = text.match(/(?:T|\s)(\d{2}):(\d{2})/) || text.match(/^(\d{1,2}):(\d{2})/);

  return {
    date: dateMatch?.[1] || "",
    time: timeMatch ? `${padTime(timeMatch[1])}:${timeMatch[2]}` : text
  };
};

const formatFlightDate = (segment) => {
  const date = segment?.date || normalizeDateTime(segment?.time).date;
  if (!date) return "";

  return date.replace(/-/g, "/");
};

const formatFlightTime = (segment) => {
  const time = normalizeDateTime(segment?.time).time;
  return time || "-";
};

const getTimezoneLabel = (timezone) => {
  return timezone.replace("Asia/", "");
};

const sleepMode = ref(true);

const toggleSleepMode = () => {
  sleepMode.value = !sleepMode.value;
};

const nextFlight = () => {
  if (!hasNextFlight.value) return;
  index.value += 1;
};

const prevFlight = () => {
  if (!hasPreviousFlight.value) return;
  index.value -= 1;
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
        :class="[
          'flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white shadow transition hover:scale-105',
          hasPreviousFlight ? 'visible pointer-events-auto' : 'invisible pointer-events-none'
        ]"
        :aria-hidden="!hasPreviousFlight"
        :tabindex="hasPreviousFlight ? 0 : -1"
      >
        <ChevronLeft class="h-7 w-7 text-[#64748B]" :stroke-width="3" />
      </button>

      <!-- Flight Card -->
      <div
        class="relative flex h-[450px] w-[50%] flex-col overflow-hidden rounded-3xl bg-[#7E99BF] shadow-xl"
      >

        <!-- 航班操作選單 -->
        <button
          type="button"
          @click.stop="flightActionMenuOpen = !flightActionMenuOpen"
          class="absolute right-4 top-4 z-20 flex h-8 w-8 items-center justify-center rounded-full bg-white/20 text-white transition hover:bg-white/30"
          title="航班操作"
        >
          <span class="text-xl leading-none">⋯</span>
        </button>
        <div
          v-if="flightActionMenuOpen"
          @click.stop
          class="absolute right-4 top-14 z-30 w-28 overflow-hidden rounded-xl border border-white/20 bg-white py-1 text-sm font-medium shadow-lg"
        >
          <button
            type="button"
            @click="openEditFlightModal"
            class="block w-full px-4 py-2 text-left text-slate-700 transition-colors hover:bg-slate-50"
          >
            編輯
          </button>
          <button
            type="button"
            @click="deleteCurrentFlight"
            class="block w-full px-4 py-2 text-left text-red-600 transition-colors hover:bg-red-50"
          >
            刪除
          </button>
        </div>

        <!-- Blue Area -->
        <div class="grid flex-1 grid-rows-[auto_1fr] p-9">

          <!-- Top -->
          <div>
            <p class="text-[11px] font-semibold tracking-[0.18em] text-[#DBE1FF]">
              FLIGHT NUMBER
            </p>

            <h2 class="mt-1 text-3xl font-bold leading-tight text-white">
              {{ flightData.flightNumber }}
            </h2>

            <p class="mt-0.5 text-sm font-medium text-[#DBE1FF]">
              {{ flightData.airline }}
            </p>
          </div>

          <!-- Route -->
          <div class="grid grid-cols-[minmax(0,1fr)_64px_minmax(0,1fr)] items-center gap-5 self-center">

            <!-- Departure -->
            <div class="grid min-h-[154px] grid-rows-[22px_58px_32px_22px_20px] text-center">
              <p class="text-sm font-medium text-[#DBE1FF]">
                起飛
              </p>

              <p
                class="flex items-center justify-center text-4xl font-black leading-none text-white"
                :title="formatLocationTitle(flightData.departure)"
              >
                {{ formatLocation(flightData.departure) }}
              </p>

              <p class="text-xl font-semibold leading-none text-white">
                {{ formatFlightTime(flightData.departure) }}
              </p>

              <p v-if="formatFlightDate(flightData.departure)" class="text-sm font-medium text-[#DBE1FF]">
                {{ formatFlightDate(flightData.departure) }}
              </p>

              <p class="truncate text-xs font-medium text-[#DBE1FF]" :title="flightData.departure.timezone">
                {{ flightData.departure.timezone }}
              </p>
            </div>

            <!-- Plane -->
            <div class="flex min-h-[154px] items-center justify-center">
              <div class="flex h-12 w-12 items-center justify-center rounded-full bg-white/20">
                <Plane class="h-6 w-6 rotate-45 text-white" />
              </div>
            </div>

            <!-- Arrival -->
            <div class="grid min-h-[154px] grid-rows-[22px_58px_32px_22px_20px] text-center">
              <p class="text-sm font-medium text-[#DBE1FF]">
                抵達
              </p>

              <p
                class="flex items-center justify-center text-4xl font-black leading-none text-white"
                :title="formatLocationTitle(flightData.arrival)"
              >
                {{ formatLocation(flightData.arrival) }}
              </p>

              <p class="text-xl font-semibold leading-none text-white">
                {{ formatFlightTime(flightData.arrival) }}
              </p>

              <p v-if="formatFlightDate(flightData.arrival)" class="text-sm font-medium text-[#DBE1FF]">
                {{ formatFlightDate(flightData.arrival) }}
              </p>

              <p class="truncate text-xs font-medium text-[#DBE1FF]" :title="flightData.arrival.timezone">
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
        :class="[
          'flex h-12 w-12 shrink-0 items-center justify-center rounded-full bg-white shadow transition hover:scale-105',
          hasNextFlight ? 'visible pointer-events-auto' : 'invisible pointer-events-none'
        ]"
        :aria-hidden="!hasNextFlight"
        :tabindex="hasNextFlight ? 0 : -1"
      >
        <ChevronRight class="h-7 w-7 text-[#64748B]" :stroke-width="3" />
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
      @click.self="closeQueryModal"
    >
      <div class="w-full max-w-md overflow-hidden rounded-2xl bg-white shadow-2xl">
        <div class="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-6 py-4">
          <h3 class="flex items-center gap-2 text-xl font-bold text-slate-800">
            <span class="inline-block h-6 w-2 rounded-full bg-[#7E99BF]"></span>
            {{ editingFlightIndex !== null ? '編輯航班' : '查詢航班' }}
          </h3>
          <button @click="closeQueryModal" class="p-1 text-slate-400 hover:text-slate-700">✕</button>
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
            @click="closeQueryModal"
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
            {{ querying ? '查詢中...' : (editingFlightIndex !== null ? '查詢並更新' : '查詢並加入') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
