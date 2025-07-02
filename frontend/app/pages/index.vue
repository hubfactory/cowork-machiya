<script setup lang="ts">
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import type { Reservation, ReservationResponse } from '@/types/reservation';
import { z } from 'zod';
import { format } from 'date-fns';

const heroImage = '/hero.jpg';
const firstDayOfWeek: any = 0;
const selectedDate = ref<string>('');
const seatInfo = ref<Record<string, number>>({
  '2024-07-01': 5,
  '2024-07-02': 0,
  '2024-07-03': 2,
  '2024-07-04': 1,
  '2024-07-05': 3,
  '2024-07-06': 0,
  '2024-07-07': 4,
});
const holidayInfo = ref<string[]>([
  '2024-07-06', '2024-07-13', '2024-07-20', '2024-07-27'
]);

// v-calendar用 attributes生成
const calendarAttrs = computed(() => {
  const attrs = [];
  for (let i = 1; i <= 31; i++) {
    const date = `2024-07-${String(i).padStart(2, '0')}`;
    if (holidayInfo.value.includes(date)) {
      attrs.push({
        key: `holiday-${date}`,
        dates: [new Date(date)],
        highlight: { color: '#a94442', fillMode: 'solid' as const },
        customData: { type: 'holiday' },
        popover: { label: '休日' }
      });
    } else if (seatInfo.value[date] !== undefined) {
      const seats = seatInfo.value[date];
      attrs.push({
        key: `seat-${date}`,
        dates: [new Date(date)],
        highlight: { color: seats === 0 ? '#a94442' : '#bfa77a', fillMode: 'outline' as const },
        customData: { type: seats === 0 ? 'full' : 'seat', seats },
        popover: { label: seats === 0 ? '満席' : `残${seats}` }
      });
    }
  }
  return attrs;
});

const onDaySelect = (date: Date) => {
  const d = format(date, 'yyyy-MM-dd');
  selectedDate.value = d;
  form.value.date = d;
};

const form = ref({
  name: '',
  email: '',
  date: '',
  seats: 1,
});
const formError = ref('');
const userEmail = ref('');
const reservations = ref<Reservation[]>([]);

const schema = z.object({
  name: z.string().min(1, '名前は必須です'),
  email: z.string().email('メールアドレス形式で入力してください'),
  date: z.string().min(1, '日付を選択してください'),
  seats: z.number().min(1, '1席以上選択してください'),
});

const submitReservation = async () => {
  formError.value = '';
  const parsed = schema.safeParse(form.value);
  if (!parsed.success) {
    formError.value = parsed.error.errors[0].message;
    return;
  }
  alert('予約しました（ダミー）');
  form.value = { name: '', email: '', date: '', seats: 1 };
};

const fetchReservations = async () => {
  if (!userEmail.value) return;
  reservations.value = [
    { id: '1', name: '山田太郎', email: userEmail.value, date: '2024-07-01', seats: 2 },
    { id: '2', name: '佐藤花子', email: userEmail.value, date: '2024-07-03', seats: 1 },
  ];
};

const cancelReservation = async (id: string) => {
  alert('キャンセルしました（ダミー）');
  reservations.value = reservations.value.filter(r => r.id !== id);
};

const { get, post, del, loading, error } = useApi();
</script>

<template>
  <div class="centered-container">
    <section class="hero">
      <div class="hero-card">
        <img :src="heroImage" alt="ヒーロー画像" class="hero-image" />
        <div class="hero-desc">
          <span class="site-title">町屋コワーキングスペース</span><br />
          歴史ある町屋をリノベーションした、落ち着きとモダンが調和した空間で快適にお過ごしください。
        </div>
      </div>
    </section>

    <section class="calendar">
      <div class="calendar-card">
        <h2 class="section-title">予約カレンダー</h2>
        <client-only>
          <!-- @ts-expect-error -->
          <VCalendar
            expanded
            :attributes="calendarAttrs"
            class="vcalendar-google"
            :title-position="'center'"
            :first-day-of-week="firstDayOfWeek"
            :show-arrows="true"
            :show-weeknumbers="false"
            :min-page="{ month: 7, year: 2024 }"
            :max-page="{ month: 7, year: 2024 }"
          >
            <template #day-content="{ day, attributes }">
              <div
                class="vc-day-content-custom"
                :class="{ 'selected-day-bg': selectedDate === format(day.date, 'yyyy-MM-dd') }"
                @click="onDaySelect(day.date)"
                style="cursor: pointer;"
              >
                <span
                  v-if="day.isToday || day.isSelected"
                  class="vc-day-highlight-custom"
                ></span>
                <span class="vc-day-label-custom">{{ day.day }}</span>
                <div v-if="attributes.length">
                  <span
                    v-for="attr in attributes.filter((a: any) => a.customData)"
                    :key="attr.key"
                    :class="[
                      'calendar-badge',
                      attr.customData.type === 'full' ? 'full' :
                      attr.customData.type === 'seat' ? 'seat' : 'holiday'
                    ]"
                  >
                    {{ attr.customData.type === 'full'
                      ? '満'
                      : attr.customData.type === 'seat'
                        ? `残${attr.customData.seats}`
                        : '休'
                    }}
                  </span>
                </div>
              </div>
            </template>
          </VCalendar>
        </client-only>
        <div v-if="selectedDate" class="selected-date">選択日: <span class="selected-badge">{{ selectedDate }}</span></div>
        <div class="calendar-legend">
          <span class="legend holiday-badge">休: 休日</span>
          <span class="legend seat-badge">残: 残席数</span>
          <span class="legend full-badge">満席</span>
        </div>
      </div>
    </section>

    <section class="reservation-form">
      <div class="form-card">
        <h2 class="section-title">予約フォーム</h2>
        <div class="selected-date">
          選択日: <span class="selected-badge">{{ selectedDate || '-' }}</span>
        </div>
        <form @submit.prevent="submitReservation" class="form-grid">
          <div class="form-group">
            <label for="name">名前</label>
            <input id="name" v-model="form.name" type="text" required class="modern-input" placeholder="例: 山田太郎" />
          </div>
          <div class="form-group">
            <label for="email">メールアドレス</label>
            <input id="email" v-model="form.email" type="email" required class="modern-input" placeholder="例: sample@example.com" />
          </div>
          <div class="form-group">
            <label for="seats">席数</label>
            <input id="seats" v-model.number="form.seats" type="number" min="1" required class="modern-input" placeholder="1" />
          </div>
          <div v-if="formError" class="form-error">
            <span class="error-text">{{ formError }}</span>
          </div>
          <button type="submit" class="modern-btn" :disabled="loading">予約</button>
        </form>
      </div>
    </section>

    <section class="reservation-list">
      <div class="list-card">
        <h2 class="section-title">予約一覧</h2>
        <form @submit.prevent="fetchReservations" class="search-form">
          <input v-model="userEmail" type="email" placeholder="メールアドレスで検索" required class="modern-input search-input" />
          <button type="submit" class="modern-btn">検索</button>
        </form>
        <ul v-if="reservations.length" class="reservation-ul">
          <li v-for="r in reservations" :key="r.id" class="reservation-li">
            <div class="reservation-info">
              <span class="date-label">{{ r.date }}</span>
              <span>{{ r.name }}</span>
              <span>{{ r.seats }}席</span>
            </div>
            <button class="modern-btn cancel-btn" @click="cancelReservation(r.id!)">キャンセル</button>
          </li>
        </ul>
        <div v-else class="no-reservation">予約がありません</div>
      </div>
    </section>
  </div>
</template>

<style lang="scss" scoped>
@use 'sass:color';
$main-bg: #fff;
$main-fg: #222;
$accent: #2c3e50;
$card-bg: #fff;
$card-border: #e0e0e0;
$modern-shadow: 0 4px 24px rgba(0,0,0,0.08);
$radius: 18px;
$badge-full: #b04a4a;
$badge-seat: #374151;
$badge-text: #fff;

.centered-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: $main-bg;
  color: $main-fg;
  min-height: 100vh;
}
.hero {
  width: 100vw;
  margin-bottom: 2rem;
  .hero-card {
    width: 100vw;
    background: $card-bg;
    border-radius: 0;
    box-shadow: none;
    overflow: hidden;
    text-align: center;
    padding-bottom: 1rem;
    margin-left: calc(-50vw + 50%);
    margin-right: calc(-50vw + 50%);
  }
  .hero-image {
    width: 100vw;
    max-width: 100vw;
    max-height: 320px;
    object-fit: cover;
    border-radius: 0;
    margin-bottom: 0.5rem;
    display: block;
  }
  .hero-desc {
    font-size: 1.1rem;
    padding: 1rem 1.2rem 0 1.2rem;
    color: $main-fg;
    .site-title {
      font-size: 1.3rem;
      font-weight: bold;
      color: $accent;
      letter-spacing: 0.1em;
    }
  }
}
.section-title {
  font-size: 1.2rem;
  font-weight: bold;
  margin-bottom: 1rem;
  color: $accent;
  letter-spacing: 0.05em;
}
.calendar, .reservation-form, .reservation-list {
  width: 100%;
  max-width: 800px;
  margin: 0 auto 2rem auto;
}
.calendar-card, .form-card, .list-card {
  background: $card-bg;
  border-radius: $radius;
  box-shadow: $modern-shadow;
  padding: 1.2rem 1rem 1.5rem 1rem;
  border: 1px solid $card-border;
}
.vcalendar-google {
  :deep(.vc-pane-container) {
    background: $card-bg;
    border-radius: $radius;
    color: $main-fg;
    font-size: 1.1rem;
    box-shadow: $modern-shadow;
    padding: 0.5rem 0.5rem 1.5rem 0.5rem;
  }
  :deep(.vc-title) {
    color: $accent;
    font-size: 1.3rem;
    font-weight: bold;
    letter-spacing: 0.05em;
  }
  :deep(.vc-day-content-custom) {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
  }
  :deep(.vc-day-highlight-custom) {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 2em;
    height: 2em;
    background: #1976d2;
    border-radius: 50%;
    z-index: 0;
    pointer-events: none;
  }
  :deep(.vc-day-label-custom) {
    position: relative;
    z-index: 1;
    font-weight: bold;
    font-size: 1.1em;
    margin-bottom: 0.2em;
    color: #fff;
    line-height: 2em;
    display: inline-block;
    text-align: center;
    width: 2em;
    height: 2em;
  }
  :deep(.selected-day-bg) {
    background: #ffe4ec !important;
    border-radius: 10px;
    transition: background 0.2s;
  }
}
.calendar-badge {
  display: inline-block;
  margin-top: 4px;
  padding: 0.15em 1.1em;
  border-radius: 8px;
  font-size: 1.05em;
  font-weight: 600;
  line-height: 1.4;
  letter-spacing: 0.02em;
  &.full, &.holiday { background: $badge-full; color: $badge-text; }
  &.seat { background: $badge-seat; color: $badge-text; }
}
.selected-date {
  margin-bottom: 0.5rem;
  .selected-badge {
    background: $accent;
    color: #fff;
    border-radius: 12px;
    padding: 0.2em 0.8em;
    font-size: 1rem;
    margin-left: 0.5em;
  }
}
.calendar-legend {
  display: flex;
  gap: 1rem;
  font-size: 1rem;
  margin-top: 0.5rem;
  .legend {
    display: inline-block;
    padding: 0.1em 1.1em;
    border-radius: 8px;
    font-weight: 600;
    font-size: 1em;
    line-height: 1.4;
    letter-spacing: 0.02em;
  }
  .holiday-badge, .full-badge { background: $badge-full; color: $badge-text; }
  .seat-badge { background: $badge-seat; color: $badge-text; }
}
.reservation-form {
  .form-grid {
    display: flex;
    flex-direction: column;
    gap: 1.2rem;
    max-width: 400px;
    margin: 0 auto;
  }
  .form-group {
    display: flex;
    flex-direction: column;
    gap: 0.4rem;
    label {
      font-size: 1rem;
      color: $accent;
      margin-bottom: 0.2rem;
    }
  }
  .modern-input {
    padding: 0.8em 1em;
    border-radius: 10px;
    border: 1px solid $card-border;
    font-size: 1.1rem;
    background: #fff;
    color: $main-fg;
    outline: none;
    transition: border 0.2s;
    &:focus {
      border: 1.5px solid $accent;
    }
  }
  .form-error {
    margin-bottom: 0.5rem;
    .error-text {
      color: #e57373;
      font-weight: bold;
    }
  }
  .modern-btn {
    background: $accent;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.9em 0;
    font-size: 1.1rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: background 0.2s;
    width: 100%;
    &:hover {
      background: color.adjust($accent, $lightness: -10%);
    }
    &:disabled {
      background: #ccc;
      color: #888;
      cursor: not-allowed;
    }
  }
}
.reservation-list {
  .search-form {
    display: flex;
    flex-direction: row;
    gap: 1rem;
    margin-bottom: 1rem;
    max-width: 400px;
    margin-left: auto;
    margin-right: auto;
    background: none;
    border-radius: 0;
    padding: 0;
    box-shadow: none;
    border: none;
  }
  .search-input {
    flex: 1;
    background: #fff;
    color: $main-fg;
    border-radius: 10px;
    font-size: 1.1rem;
    padding: 0.8em 1em;
    border: 1px solid $card-border;
    outline: none;
    transition: border 0.2s;
    &:focus {
      border: 1.5px solid $accent;
    }
  }
  .modern-btn {
    background: $accent;
    color: #fff;
    border: none;
    border-radius: 10px;
    padding: 0.9em 0;
    font-size: 1.1rem;
    font-weight: bold;
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: background 0.2s;
    width: auto;
    min-width: 100px;
    &:hover {
      background: color.adjust($accent, $lightness: -10%);
    }
    &:disabled {
      background: #ccc;
      color: #888;
      cursor: not-allowed;
    }
  }
  .reservation-ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .reservation-li {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.7rem 0;
    border-bottom: 1px solid #3a362f;
  }
  .reservation-info {
    display: flex;
    gap: 1.5rem;
    align-items: center;
    .date-label {
      color: $accent;
      font-weight: bold;
    }
  }
  .modern-btn.cancel-btn {
    background: #a94442;
    color: #fff;
    font-size: 1rem;
    padding: 0.6em 1.2em;
    border-radius: 8px;
    width: auto;
    min-width: 80px;
    &:hover {
      background: color.adjust(#a94442, $lightness: -10%);
    }
  }
  .no-reservation {
    text-align: center;
    color: #888;
    padding: 1rem 0;
  }
}
</style>
