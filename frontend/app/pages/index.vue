<script setup lang="ts">
import { ref, computed } from 'vue';
import { useApi } from '@/composables/useApi';
import type { Reservation, ReservationResponse } from '@/types/reservation';
import { z } from 'zod';
import { format } from 'date-fns';

// API通信
const { get, post, del, loading, error } = useApi();

// ヒーロー画像（assetsに画像があれば差し替え）
const heroImage = '/hero.jpg';

// カレンダー関連
const today = new Date();
const selectedDate = ref<string>('');
const seatInfo = ref<Record<string, number>>({});
const holidayInfo = ref<string[]>([]);

// 予約フォーム
const form = ref({
  name: '',
  email: '',
  date: '',
  seats: 1,
});
const formError = ref('');

// 予約一覧
const userEmail = ref('');
const reservations = ref<Reservation[]>([]);

// バリデーションスキーマ
const schema = z.object({
  name: z.string().min(1, '名前は必須です'),
  email: z.string().email('メールアドレス形式で入力してください'),
  date: z.string().min(1, '日付を選択してください'),
  seats: z.number().min(1, '1席以上選択してください'),
});

// カレンダーから日付選択
function onDateSelect(day: { date: Date }) {
  const d = format(day.date, 'yyyy-MM-dd');
  selectedDate.value = d;
  form.value.date = d;
}

// 予約送信
async function submitReservation() {
  formError.value = '';
  const parsed = schema.safeParse(form.value);
  if (!parsed.success) {
    formError.value = parsed.error.errors[0].message;
    return;
  }
  const res = await post<Reservation>('/api/reservations', form.value);
  if (res) {
    alert('予約しました');
    form.value = { name: '', email: '', date: '', seats: 1 };
    // 必要ならカレンダー・予約一覧を再取得
  } else {
    formError.value = error.value || '予約に失敗しました';
  }
}

// 予約一覧取得
async function fetchReservations() {
  if (!userEmail.value) return;
  const res = await get<ReservationResponse>('/api/reservations/', { email: userEmail.value });
  reservations.value = res?.reservations || [];
}

// 予約キャンセル
async function cancelReservation(id: string) {
  const res = await del(`/api/reservations/${id}`);
  if (res) {
    alert('キャンセルしました');
    fetchReservations();
  }
}
</script>

<template>
  <section class="hero">
    <img :src="heroImage" alt="ヒーロー画像" class="hero-image" />
    <div class="hero-desc">コワーキングスペースの説明文</div>
  </section>

  <section class="calendar">
    <v-calendar
      is-expanded
      :attributes="[]"
      @dayclick="onDateSelect"
    />
    <div v-if="selectedDate">選択日: {{ selectedDate }}</div>
  </section>

  <section class="reservation-form">
    <h2>予約フォーム</h2>
    <form @submit.prevent="submitReservation">
      <div>
        <label>名前</label>
        <input v-model="form.name" type="text" required />
      </div>
      <div>
        <label>メールアドレス</label>
        <input v-model="form.email" type="email" required />
      </div>
      <div>
        <label>日付</label>
        <input v-model="form.date" type="date" required />
      </div>
      <div>
        <label>席数</label>
        <input v-model.number="form.seats" type="number" min="1" required />
      </div>
      <div v-if="formError" class="form-error">{{ formError }}</div>
      <button type="submit" :disabled="loading">予約</button>
    </form>
  </section>

  <section class="reservation-list">
    <h2>予約一覧</h2>
    <form @submit.prevent="fetchReservations">
      <input v-model="userEmail" type="email" placeholder="メールアドレスで検索" required />
      <button type="submit">検索</button>
    </form>
    <ul>
      <li v-for="r in reservations" :key="r.id">
        {{ r.date }} / {{ r.name }} / {{ r.seats }}席
        <button @click="cancelReservation(r.id!)">キャンセル</button>
      </li>
    </ul>
  </section>
</template>

<style lang="scss" scoped>
.hero {
  margin-bottom: 2rem;
  .hero-image {
    width: 100%;
    max-height: 300px;
    object-fit: cover;
    margin-bottom: 1rem;
  }
  .hero-desc {
    font-size: 1.2rem;
    margin-bottom: 1rem;
  }
}
.calendar {
  margin-bottom: 2rem;
}
.reservation-form {
  margin-bottom: 2rem;
  form > div {
    margin-bottom: 0.5rem;
  }
  .form-error {
    color: red;
    margin-bottom: 0.5rem;
  }
}
.reservation-list {
  margin-bottom: 2rem;
}
</style>
