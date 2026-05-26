<template>
  <div class="min-h-screen bg-[#f4f7fb] px-[8vw] pb-10 font-sans text-[#263245] max-[900px]:px-4 max-[900px]:pb-[30px]">

    <div
      class="h-[190px] rounded-b-[24px] bg-[linear-gradient(to_bottom,rgba(255,255,255,0),rgba(255,255,255,.15)),url('https://images.unsplash.com/photo-1570459027562-4a916cc6113f?q=80&w=1400')] bg-cover bg-center max-[900px]:h-[150px]"
    ></div>

    <section class="mt-3 grid grid-cols-2 gap-[14px] max-[900px]:grid-cols-1">
      <div class="flex h-[70px] items-center rounded-[22px] border-[1.5px] border-[#94a9c5] bg-white px-[22px] shadow-[0_8px_20px_rgba(49,74,107,.06)]">
        <span class="mr-4 text-[26px]">📍</span>
        <div>
          <h1 class="text-2xl font-bold">Tokyo, Japan</h1>
          <p class="mt-1 text-[15px] text-slate-500">2026/06/14-2026/06/19・共6天</p>
        </div>
      </div>

      <div class="relative h-[70px] rounded-[22px] border-[1.5px] border-[#94a9c5] bg-white px-[22px] pt-2.5 shadow-[0_8px_20px_rgba(49,74,107,.06)]">
        <p class="text-[13px] text-[#7b8ba1]">行程筆記：</p>
        <div class="mt-2.5 h-px bg-[#9aabc2]"></div>
        <div class="mt-2.5 h-px w-[82%] bg-[#9aabc2]"></div>
        <button class="absolute right-[18px] top-5 bg-transparent text-2xl text-[#8da0bb]">
          ✎
        </button>
      </div>
    </section>

    <section class="mt-[14px] grid grid-cols-4 gap-[14px] max-[900px]:grid-cols-1">
      <div
        v-for="card in summaryCards"
        :key="card.title"
        class="relative h-[120px] rounded-[22px] bg-white p-4 shadow-[0_8px_20px_rgba(49,74,107,.06)]"
      >
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2.5 text-[13px] text-[#7f8fa7]">
            <span class="h-[34px] w-[34px] rounded-full bg-[#70839d]"></span>
            {{ card.title }}
          </div>

          <strong v-if="card.count">{{ card.count }}</strong>
        </div>

        <h3 v-if="card.heading" class="mt-[14px] text-lg font-bold">
          {{ card.heading }}
        </h3>

        <p
          v-for="text in card.texts"
          :key="text"
          class="mt-2 text-[13px] text-[#66768d]"
        >
          {{ text }}
        </p>

        <button
          v-if="card.showPlus"
          class="absolute bottom-3 right-4 flex h-9 w-9 items-center justify-center rounded-full bg-[#27c77a] text-2xl text-white transition hover:scale-110 hover:bg-[#1fb86d]"
        >
          ＋
        </button>
      </div>
    </section>

    <section
      class="mt-4 flex w-full gap-[14px] overflow-x-auto pb-2.5
      [&::-webkit-scrollbar]:h-2
      [&::-webkit-scrollbar-thumb]:rounded-full
      [&::-webkit-scrollbar-thumb]:bg-[#c4cfdd]"
    >
      <div
        v-for="day in days"
        :key="day.id"
        class="flex h-[500px] w-[calc((100%-42px)/4)] min-w-[280px] shrink-0 flex-col rounded-[22px] bg-white p-[18px] shadow-[0_8px_20px_rgba(49,74,107,.06)] max-[900px]:w-full"
      >
        <div class="flex items-start justify-between">
          <div>
            <h2 class="text-[22px] font-bold">{{ day.title }}</h2>
            <p class="mt-1 text-xs text-[#8ea0b8]">{{ day.date }}</p>
          </div>

          <span class="text-[28px]">{{ day.weather }}</span>
        </div>

        <div
          class="mt-[14px] flex-1 overflow-y-auto pr-1
          [&::-webkit-scrollbar]:w-[5px]
          [&::-webkit-scrollbar-thumb]:rounded-full
          [&::-webkit-scrollbar-thumb]:bg-[#cbd5e2]"
        >
          <div
            v-for="(item, index) in day.items"
            :key="index"
            class="relative mb-5 border-l border-dashed border-[#a2b3c8] pl-5"
          >
            <div class="absolute left-[-5px] top-[6px] h-2 w-2 rounded-full bg-[#1f2d44]"></div>

            <div class="mb-2 text-[13px] font-bold">
              {{ item.time }}
            </div>

            <div class="flex min-h-[92px] items-center gap-3 rounded-[14px] bg-[#f6f8fb] p-[14px]">
              <img
                :src="item.image"
                class="h-[72px] w-[72px] shrink-0 rounded-lg object-cover"
              />

              <div class="min-w-0 flex-1">
                <h3 class="truncate text-lg font-bold">{{ item.name }}</h3>
                <p class="mt-1.5 text-xs text-[#8494aa]">{{ item.stay }}</p>
              </div>
            </div>

            <div class="mt-2.5 text-xs text-[#8798af]">
              🚆 {{ item.move }}
            </div>
          </div>
        </div>
      </div>
    </section>

  </div>
</template>

<script setup>
const summaryCards = [
  {
    title: '航班資訊',
    heading: 'CI108 中華航空',
    texts: ['TPE 14:35 → NRT 19:00']
  },
  {
    title: '準備清單',
    count: 31,
    texts: ['○ 電子交通卡（Suica）', '○ 大容量行動電源與充電線'],
    showPlus: true
  },
  {
    title: '購物清單',
    count: 12,
    texts: ['○ Sugar Butter Tree 楓糖口味', '○ 花王蒸氣眼罩'],
    showPlus: true
  },
  {
    title: '即時匯率',
    heading: '1 TWD = 4.65 JPY',
    texts: ['最後更新：1小時前']
  }
]

const days = [
  {
    id: 1,
    title: 'Day 1',
    date: '06.14 (Sun)',
    weather: '☀️',
    items: [
      {
        time: '19:00',
        name: '成田國際機場',
        stay: '停留01時00分',
        move: '00時46分',
        image: 'https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=200'
      },
      {
        time: '19:46',
        name: '日暮里',
        stay: '停留00時00分',
        move: '00時46分',
        image: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=200'
      },
      {
        time: '20:30',
        name: '上野',
        stay: '停留01時00分',
        move: '00時15分',
        image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=200'
      }
    ]
  },
  {
    id: 2,
    title: 'Day 2',
    date: '06.15 (Mon)',
    weather: '🌥️',
    items: [
      {
        time: '09:00',
        name: '淺草寺',
        stay: '停留02時00分',
        move: '00時20分',
        image: 'https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=200'
      },
      {
        time: '13:00',
        name: '秋葉原',
        stay: '停留03時00分',
        move: '00時30分',
        image: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=200'
      }
    ]
  },
  {
    id: 3,
    title: 'Day 3',
    date: '06.16 (Tus)',
    weather: '🌬️',
    items: [
      {
        time: '10:00',
        name: '新宿',
        stay: '停留02時00分',
        move: '00時15分',
        image: 'https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=200'
      },
      {
        time: '15:00',
        name: '原宿',
        stay: '停留02時00分',
        move: '00時25分',
        image: 'https://images.unsplash.com/photo-1513407030348-c983a97b98d8?w=200'
      }
    ]
  },
  {
    id: 4,
    title: 'Day 4',
    date: '06.17 (Wed)',
    weather: '☔',
    items: [
      {
        time: '09:00',
        name: '東京車站',
        stay: '停留01時30分',
        move: '00時20分',
        image: 'https://images.unsplash.com/photo-1533929736458-ca588d08c8be?w=200'
      },
      {
        time: '13:00',
        name: '台場',
        stay: '停留03時00分',
        move: '00時35分',
        image: 'https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=200'
      }
    ]
  },
  {
    id: 5,
    title: 'Day 5',
    date: '06.18 (Thu)',
    weather: '☀️',
    items: [
      {
        time: '10:00',
        name: '澀谷',
        stay: '停留02時00分',
        move: '00時20分',
        image: 'https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=200'
      }
    ]
  }
]
</script>