<template>
  <div class="page">

    <div class="hero"></div>

    <section class="trip-header">

      <div class="destination card">
        <span class="icon">📍</span>

        <div>
          <h1>Tokyo, Japan</h1>
          <p>2026/06/14-2026/06/19・共6天</p>
        </div>
      </div>

      <div class="note card">
        <p>行程筆記：</p>

        <div class="line"></div>
        <div class="line short"></div>

        <button class="edit-btn">✎</button>
      </div>

    </section>

    <section class="summary-grid">

      <div class="info-card">

        <div class="top">
          <div class="title">
            <span class="circle"></span>
            航班資訊
          </div>
        </div>

        <h3>CI108 中華航空</h3>
        <p>TPE 14:35 → NRT 19:00</p>

      </div>

      <div class="info-card">

        <div class="top">
          <div class="title">
            <span class="circle"></span>
            準備清單
          </div>

          <strong>31</strong>
        </div>

        <p>○ 電子交通卡（Suica）</p>
        <p>○ 大容量行動電源與充電線</p>

        <button class="plus-btn">＋</button>

      </div>

      <div class="info-card">

        <div class="top">
          <div class="title">
            <span class="circle"></span>
            購物清單
          </div>

          <strong>12</strong>
        </div>

        <p>○ Sugar Butter Tree 楓糖口味</p>
        <p>○ 花王蒸氣眼罩</p>

        <button class="plus-btn">＋</button>

      </div>

      <div class="info-card">

        <div class="top">
          <div class="title">
            <span class="circle"></span>
            即時匯率
          </div>
        </div>

        <h3>1 TWD = 4.65 JPY</h3>
        <p>最後更新：1小時前</p>

      </div>

    </section>

    <section class="days-scroll">

      <div
        class="day-card"
        v-for="day in days"
        :key="day.id"
      >

        <div class="day-head">

          <div>
            <h2>{{ day.title }}</h2>
            <p>{{ day.date }}</p>
          </div>

          <span class="weather">{{ day.weather }}</span>

        </div>

        <div class="timeline">

          <div
            class="timeline-item"
            v-for="(item,index) in day.items"
            :key="index"
          >

            <div class="dot"></div>

            <div class="time">
              {{ item.time }}
            </div>

            <div class="place-card">

              <img :src="item.image">

              <div class="place-info">
                <h3>{{ item.name }}</h3>
                <p>{{ item.stay }}</p>
              </div>

            </div>

            <div class="move">
              🚆 {{ item.move }}
            </div>

          </div>

        </div>

      </div>

    </section>

  </div>
</template>

<script setup>

const days = [

  {
    id:1,
    title:"Day 1",
    date:"06.14 (Sun)",
    weather:"☀️",

    items:[
      {
        time:"19:00",
        name:"成田國際機場",
        stay:"停留01時00分",
        move:"00時46分",
        image:"https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=200"
      },

      {
        time:"19:46",
        name:"日暮里",
        stay:"停留00時00分",
        move:"00時46分",
        image:"https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=200"
      },

      {
        time:"20:30",
        name:"上野",
        stay:"停留01時00分",
        move:"00時15分",
        image:"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=200"
      },

      {
        time:"20:30",
        name:"上野",
        stay:"停留01時00分",
        move:"00時15分",
        image:"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=200"
      },

      {
        time:"20:30",
        name:"上野",
        stay:"停留01時00分",
        move:"00時15分",
        image:"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=200"
      },

      {
        time:"20:30",
        name:"上野",
        stay:"停留01時00分",
        move:"00時15分",
        image:"https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?w=200"
      }
    ]
  },

  {
    id:2,
    title:"Day 2",
    date:"06.15 (Mon)",
    weather:"🌥️",

    items:[
      {
        time:"09:00",
        name:"淺草寺",
        stay:"停留02時00分",
        move:"00時20分",
        image:"https://images.unsplash.com/photo-1528360983277-13d401cdc186?w=200"
      },

      {
        time:"13:00",
        name:"秋葉原",
        stay:"停留03時00分",
        move:"00時30分",
        image:"https://images.unsplash.com/photo-1542051841857-5f90071e7989?w=200"
      }
    ]
  },

  {
    id:3,
    title:"Day 3",
    date:"06.16 (Tus)",
    weather:"🌬️",

    items:[
      {
        time:"10:00",
        name:"新宿",
        stay:"停留02時00分",
        move:"00時15分",
        image:"https://images.unsplash.com/photo-1536098561742-ca998e48cbcc?w=200"
      },

      {
        time:"15:00",
        name:"原宿",
        stay:"停留02時00分",
        move:"00時25分",
        image:"https://images.unsplash.com/photo-1513407030348-c983a97b98d8?w=200"
      }
    ]
  },

  {
    id:4,
    title:"Day 4",
    date:"06.17 (Wed)",
    weather:"☔",

    items:[
      {
        time:"09:00",
        name:"東京車站",
        stay:"停留01時30分",
        move:"00時20分",
        image:"https://images.unsplash.com/photo-1533929736458-ca588d08c8be?w=200"
      },

      {
        time:"13:00",
        name:"台場",
        stay:"停留03時00分",
        move:"00時35分",
        image:"https://images.unsplash.com/photo-1503899036084-c55cdd92da26?w=200"
      }
    ]
  }

]

</script>

<style scoped>

*{
  box-sizing:border-box;
  margin:0;
  padding:0;
}

.page{
  background:#f4f7fb;
  min-height:100vh;
  padding:0 8vw 40px;
  font-family:Arial,"Noto Sans TC",sans-serif;
  color:#263245;
}

.hero{
  height:190px;
  border-radius:0 0 24px 24px;
  background:
  linear-gradient(to bottom,rgba(255,255,255,0),rgba(255,255,255,.15)),
  url("https://images.unsplash.com/photo-1570459027562-4a916cc6113f?q=80&w=1400")
  center/cover;
}

.trip-header{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:14px;
  margin-top:12px;
}

.card{
  background:white;
  border-radius:22px;
  box-shadow:0 8px 20px rgba(49,74,107,.06);
}

.destination,
.note{
  height:70px;
  border:1.5px solid #94a9c5;
  display:flex;
  align-items:center;
  padding:0 22px;
}

.destination .icon{
  font-size:26px;
  margin-right:16px;
}

.destination h1{
  font-size:24px;
}

.destination p{
  font-size:15px;
  color:#64748b;
  margin-top:4px;
}

.note{
  position:relative;
  display:block;
  padding-top:10px;
}

.note p{
  font-size:13px;
  color:#7b8ba1;
}

.line{
  height:1px;
  background:#9aabc2;
  margin-top:10px;
}

.short{
  width:82%;
}

.edit-btn{
  position:absolute;
  right:18px;
  top:20px;
  font-size:24px;
  color:#8da0bb;
  background:none;
  border:none;
  cursor:pointer;
}

.summary-grid{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:14px;
  margin-top:14px;
}

.info-card{
  position:relative;
  height:120px;
  padding:16px;
  border-radius:22px;
  background:white;
  box-shadow:0 8px 20px rgba(49,74,107,.06);
}

.top{
  display:flex;
  justify-content:space-between;
  align-items:center;
}

.title{
  display:flex;
  align-items:center;
  gap:10px;
  font-size:13px;
  color:#7f8fa7;
}

.circle{
  width:34px;
  height:34px;
  border-radius:50%;
  background:#70839d;
}

.info-card h3{
  margin-top:14px;
  font-size:18px;
}

.info-card p{
  margin-top:8px;
  font-size:13px;
  color:#66768d;
}

.plus-btn{
  position:absolute;
  right:16px;
  bottom:12px;

  width:36px;
  height:36px;
  border:none;
  border-radius:50%;

  background:#27c77a;
  color:white;

  font-size:24px;
  cursor:pointer;

  display:flex;
  align-items:center;
  justify-content:center;

  transition:.2s;
}

.plus-btn:hover{
  transform:scale(1.08);
  background:#1fb86d;
}

.days-scroll{
  display:flex;
  gap:14px;
  overflow-x:auto;
  margin-top:16px;
  padding-bottom:10px;
  scroll-snap-type:x mandatory;
}

.days-scroll::-webkit-scrollbar{
  height:8px;
}

.days-scroll::-webkit-scrollbar-thumb{
  background:#c4cfdd;
  border-radius:999px;
}

.day-card{
  flex:0 0 280px;
  display:flex;
  flex-direction:column;
  height:500px;
  background:white;
  border-radius:22px;
  padding:18px;
  box-shadow:0 8px 20px rgba(49,74,107,.06);
  scroll-snap-align:start;
}

.day-head{
  display:flex;
  justify-content:space-between;
  align-items:flex-start;
}

.day-head h2{
  font-size:22px;
}

.day-head p{
  margin-top:4px;
  font-size:12px;
  color:#8ea0b8;
}

.weather{
  font-size:28px;
}

.timeline{
  flex:1;
  overflow-y:auto;
  margin-top:14px;
  padding-right:4px;
}

.timeline::-webkit-scrollbar{
  width:5px;
}

.timeline::-webkit-scrollbar-thumb{
  background:#cbd5e2;
  border-radius:999px;
}

.timeline-item{
  position:relative;
  border-left:1px dashed #a2b3c8;
  padding-left:18px;
  margin-bottom:20px;
}

.dot{
  position:absolute;
  left:-4px;
  top:2px;
  width:8px;
  height:8px;
  border-radius:50%;
  background:#1f2d44;
}

.time{
  font-size:13px;
  font-weight:bold;
  margin-bottom:8px;
}

.place-card{
  display:flex;
  gap:12px;
  background:#f6f8fb;
  border-radius:14px;
  padding:14px;
  min-height:92px;
}

.place-card img{
  width:72px;
  height:72px;
  object-fit:cover;
  border-radius:8px;
}

.place-info h3{
  font-size:18px;
}

.place-info p{
  margin-top:6px;
  font-size:12px;
  color:#8494aa;
}

.move{
  margin-top:10px;
  font-size:12px;
  color:#8798af;
}

@media(max-width:900px){

  .page{
    padding:0 16px 30px;
  }

  .trip-header{
    grid-template-columns:1fr;
  }

  .summary-grid{
    grid-template-columns:1fr;
  }

  .hero{
    height:150px;
  }

}

</style>