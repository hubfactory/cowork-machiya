<script setup lang="ts">
import { ref } from 'vue';
import Calendar from '@/components/Calendar.vue';
import { useApi } from '@/composables/useApi';
import type { Reservation } from '@/types/reservation';

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
const selectedDate = ref('');

const defaultSeat = ref<number>(10);
const defaultHolidays = ref<string[]>([]);
const daysOfWeek = ['日', '月', '火', '水', '木', '金', '土'];
const { get, post, loading, error } = useApi();

const month = ref<string>('');
const reservations = ref<Reservation[]>([]);
const reservationError = ref('');

const saveDefaultSettings = async () => {
  // バリデーション
  if (defaultSeat.value < 1) {
    alert('席数は1以上で入力してください');
    return;
  }
  // デフォルト席数保存
  const seatRes = await post('/api/admin/default_seat', { seats: defaultSeat.value });
  // デフォルト休日保存
  const holidayRes = await post('/api/admin/default_holiday', { holidays: defaultHolidays.value });
  if (seatRes && holidayRes) {
    alert('保存しました');
  } else {
    alert('保存に失敗しました');
  }
};

const fetchReservations = async () => {
  reservationError.value = '';
  if (!month.value) {
    reservationError.value = '月を選択してください';
    return;
  }
  const [year, m] = month.value.split('-');
  const res = await get<{ reservations: Reservation[] }>('/api/admin/reservations/', { 'yyyy/MM': `${year}/${m}` });
  if (res && res.reservations) {
    reservations.value = res.reservations;
  } else {
    reservations.value = [];
    reservationError.value = error.value || '取得に失敗しました';
  }
};
</script>

<template>
  <div class="centered-container">
    <section class="admin-auth">
      <!-- ベーシック認証（実装は後ほど） -->
      <div>[ベーシック認証]</div>
    </section>

    <section class="admin-settings">
      <div class="form-card">
        <h2 class="section-title">基本設定</h2>
        <form @submit.prevent="saveDefaultSettings" class="form-grid">
          <div class="form-group">
            <label for="default-seat">デフォルト席数</label>
            <input id="default-seat" v-model.number="defaultSeat" type="number" min="1" class="modern-input" placeholder="例: 10" />
          </div>
          <div class="form-group">
            <label>デフォルト休日（複数選択可）</label>
            <div class="weekday-checkboxes">
              <label v-for="day in daysOfWeek" :key="day" class="checkbox-label">
                <input type="checkbox" :value="day" v-model="defaultHolidays" />
                {{ day }}
              </label>
            </div>
          </div>
          <div v-if="error" class="form-error">
            <span class="error-text">{{ error }}</span>
          </div>
          <button type="submit" class="modern-btn" :disabled="loading">保存</button>
        </form>
      </div>
    </section>

    <section class="admin-calendar">
      <Calendar
        :seat-info="seatInfo"
        :holiday-info="holidayInfo"
        v-model="selectedDate"
        :min-page="{ month: 7, year: 2024 }"
        :max-page="{ month: 7, year: 2024 }"
        :first-day-of-week="0"
        admin-mode
      />
    </section>

    <section class="admin-reservations">
      <div class="list-card">
        <h2 class="section-title">予約一覧</h2>
        <form @submit.prevent="fetchReservations" class="search-form">
          <input v-model="month" type="month" required class="modern-input search-input" />
          <button type="submit" class="modern-btn">検索</button>
        </form>
        <div v-if="reservationError" class="form-error"><span class="error-text">{{ reservationError }}</span></div>
        <ul v-if="reservations.length" class="reservation-ul">
          <li v-for="r in reservations" :key="r.id" class="reservation-li">
            <div class="reservation-info">
              <span class="date-label">{{ r.date }}</span>
              <span>{{ r.name }}</span>
              <span>{{ r.email }}</span>
              <span>{{ r.seats }}席</span>
            </div>
          </li>
        </ul>
        <div v-else-if="!reservationError" class="no-reservation">予約がありません</div>
      </div>
    </section>
  </div>
</template>

<style lang="scss" scoped>
.centered-container {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
section {
  width: 100%;
}
.admin-auth {
  margin-bottom: 2rem;
}
.admin-settings {
  margin-bottom: 2rem;
}
.admin-calendar {
  margin-bottom: 2rem;
}
.form-card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 1.2rem 1rem 1.5rem 1rem;
  border: 1px solid #e0e0e0;
  margin: 0 auto 2rem auto;
  width: 100%;
}
.form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  label {
    font-size: 1rem;
    color: #2c3e50;
    margin-bottom: 0.2rem;
  }
}
.modern-input {
  padding: 0.8em 1em;
  border-radius: 10px;
  border: 1px solid #e0e0e0;
  font-size: 1.1rem;
  background: #fff;
  color: #222;
  outline: none;
  transition: border 0.2s;
  &:focus {
    border: 1.5px solid #2c3e50;
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
  background: #2c3e50;
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
  min-width: 120px;
  margin: 0 auto;
  &:hover {
    background: #1a2533;
  }
  &:disabled {
    background: #ccc;
    color: #888;
    cursor: not-allowed;
  }
}
.weekday-checkboxes {
  display: flex;
  gap: 0.7em;
  flex-wrap: wrap;
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.2em;
  font-size: 1.1em;
}
.calendar-card {
  width: 100%;
}
.list-card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
  padding: 1.2rem 1rem 1.5rem 1rem;
  border: 1px solid #e0e0e0;
  width: 100%;
  margin-bottom: 2rem;
}
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
  color: #222;
  border-radius: 10px;
  font-size: 1.1rem;
  padding: 0.8em 1em;
  border: 1px solid #e0e0e0;
  outline: none;
  transition: border 0.2s;
  &:focus {
    border: 1.5px solid #2c3e50;
  }
}
.reservation-ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.reservation-li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.7em 0;
  border-bottom: 1px solid #e0e0e0;
  font-size: 1.08em;
}
.reservation-info {
  display: flex;
  gap: 1.2em;
  align-items: center;
}
.date-label {
  font-weight: bold;
  color: #2c3e50;
  margin-right: 0.7em;
}
.no-reservation {
  text-align: center;
  color: #888;
  margin-top: 1.2em;
}
</style>
