<script setup lang="ts">
// 管理画面用のロジックや型定義、API通信などを記述予定
</script>

<template>
  <section class="admin-auth">
    <!-- ベーシック認証（実装は後ほど） -->
    <div>[ベーシック認証]</div>
  </section>

  <section class="admin-settings">
    <!-- 基本設定：デフォルト席数・休日設定 -->
    <div>[基本設定フォーム]</div>
  </section>

  <section class="admin-calendar">
    <!-- カレンダー：日毎の席数・休日設定 -->
    <div>[管理用カレンダー]</div>
  </section>

  <section class="admin-reservations">
    <!-- 予約一覧：月単位で表示 -->
    <div>[予約一覧（マンスピッカー）]</div>
  </section>
</template>

<style lang="scss" scoped>
.admin-auth {
  margin-bottom: 2rem;
}
.admin-settings {
  margin-bottom: 2rem;
}
.admin-calendar {
  margin-bottom: 2rem;
}
</style>
