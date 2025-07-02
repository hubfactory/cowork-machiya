<script setup lang="ts">
import { ref, computed, watch, defineProps, defineEmits } from 'vue';
import { format } from 'date-fns';

// v-calendarの型をローカルで定義
interface PageAddress { month: number; year: number; }
type DayOfWeek = number;

const props = defineProps<{
  seatInfo: Record<string, number>;
  holidayInfo: string[];
  modelValue?: string;
  minPage?: PageAddress;
  maxPage?: PageAddress;
  adminMode?: boolean;
  firstDayOfWeek?: DayOfWeek;
}>();

const emit = defineEmits(['update:modelValue', 'day-select']);

const selectedDate = ref(props.modelValue ?? '');
watch(() => props.modelValue, (val) => { selectedDate.value = val ?? ''; });

const minPage = computed<PageAddress>(() => props.minPage ?? { month: 7, year: 2024 });
const maxPage = computed<PageAddress>(() => props.maxPage ?? { month: 7, year: 2024 });
const firstDayOfWeek = props.firstDayOfWeek ?? 0;

const calendarAttrs = computed(() => {
  const attrs = [];
  for (let i = 1; i <= 31; i++) {
    const date = `${minPage.value.year}-${String(minPage.value.month).padStart(2, '0')}-${String(i).padStart(2, '0')}`;
    if (props.holidayInfo.includes(date)) {
      attrs.push({
        key: `holiday-${date}`,
        dates: [new Date(date)],
        highlight: { color: '#a94442', fillMode: 'solid' as const },
        customData: { type: 'holiday' },
        popover: { label: '休日' }
      });
    } else if (props.seatInfo[date] !== undefined) {
      const seats = props.seatInfo[date];
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
  emit('update:modelValue', d);
  emit('day-select', d);
};
</script>

<template>
  <div class="calendar-card">
    <client-only>
      <!-- @ts-expect-error -->
      <VCalendar
        expanded
        :attributes="calendarAttrs"
        class="vcalendar-google"
        :title-position="'center'"
        :first-day-of-week="firstDayOfWeek as any"
        :show-arrows="true"
        :show-weeknumbers="false"
        :min-page="minPage"
        :max-page="maxPage"
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
    <slot v-if="adminMode" name="admin-tools" :selected-date="selectedDate" />
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

.calendar-card {
  background: $card-bg;
  border-radius: $radius;
  box-shadow: $modern-shadow;
  padding: 1.2rem 1rem 1.5rem 1rem;
  border: 1px solid $card-border;
  margin-bottom: 2rem;
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
</style> 