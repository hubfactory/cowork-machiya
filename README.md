# コワーキングスペース予約サイト 仕様書

## 1. システム概要

コワーキングスペースの予約をWeb上で受け付け、管理者が席数や休日を柔軟に設定できるシステム。  
ユーザーはカレンダーから空き状況を確認し、予約・キャンセルが可能。  
管理者は予約状況の確認や、席数・休日の設定ができる。

---

## 2. システム構成

### 2.1 フロントエンド

- **フレームワーク**: Nuxt.js v3
- **言語**: TypeScript
- **UIライブラリ**: @nuxt/ui
- **CSS**: 各vueファイル内にSCSSで記載（Tailwindは不使用）
- **日付処理**: date-fns
- **アイコン**: nuxt-icon
- **カレンダー**: v-calendar（推奨。もしくはvue-datepicker。より良いものがあれば提案）
- **フォームバリデーション**: zod
- **composables**:
  - API通信
  - トースト表示
  - ローディング表示
  - レスポンシブ表示（vueuseのuseMediaQuery利用）
  - 必要に応じて他の共通処理
- **型定義**: typesフォルダに集約
- **vueファイル記述順**: script → template → style

### 2.2 バックエンド

- **言語**: Python（FastAPI）
- **DB**: DynamoDB
- **サーバーレス**: AWS Lambda

---

## 3. 画面仕様

### 3.1 ユーザー画面（`app/pages/index.vue`）

- ヒーロー部分：写真＋説明
- 予約カレンダー：日毎の残席数・休日表示
- 予約フォーム：名前、メールアドレス、日付、席数
  - カレンダー日付クリックでフォーム日付自動入力
  - 予約ボタンで予約（完了時トースト表示）
- 予約一覧：メールアドレス入力でその人の予約一覧表示
  - キャンセルボタンで予約削除

### 3.2 管理画面（`app/pages/admin/index.vue`）

- ベーシック認証
- 基本設定：デフォルト席数・休日（曜日）設定
- カレンダー：日毎の席数・休日設定
- 予約一覧：月単位で表示（マンスピッカー）

---

## 4. API仕様

### 4.1 ユーザー画面用

| メソッド | エンドポイント | パラメータ | 概要 |
|---|---|---|---|
| GET | /api/seat/ | yyyy/MM | 月ごとの席数一覧取得 |
| GET | /api/holiday/ | yyyy/MM | 月ごとの休日一覧取得 |
| POST | /api/reservations | 予約情報 | 予約登録 |
| GET | /api/reservations/ | email | ユーザー予約一覧取得 |
| DELETE | /api/reservations/{id} | 予約ID | 予約削除 |

### 4.2 管理画面用

| メソッド | エンドポイント | パラメータ | 概要 |
|---|---|---|---|
| GET | /api/admin/reservations/ | yyyy/MM | 月ごとの予約一覧取得 |
| POST | /api/admin/default_holiday | 休日情報 | デフォルト休日登録 |
| POST | /api/admin/default_seat | 席数情報 | デフォルト席数登録 |
| POST | /api/holiday | 休日情報 | 休日登録 |
| POST | /api/seat/ | 席数情報 | 日毎の席数登録 |

---

## 5. 予約仕様

- 予約は1日単位（時間単位ではない）
- 席数を超えた場合は予約不可
- 予約時に「予約しました」とトースト表示

---

## 6. セキュリティ・個人情報

- メールアドレスはDynamoDBに保存
- **対策案**:
  - 通信は必ずHTTPS
  - メールアドレスはハッシュ化保存も検討（ただし予約一覧取得のため検索性も考慮）
  - 管理画面はベーシック認証＋IP制限も推奨
  - APIのレートリミット
  - 不要な個人情報は保存しない

---

## 7. ディレクトリ構成（例）

```
/app
  /pages
    index.vue
    /admin
      index.vue
  /components
  /composables
  /layouts
  /constants
  /types
  /assets
  /public
  /utils
  app.vue
  error.vue
```

---

## 8. 使用ライブラリ一覧

- Nuxt.js v3
- @nuxt/ui
- nuxt-icon
- v-calendar
- date-fns
- zod
- vueuse

---

## 9. その他

- composablesはAPI通信、トースト、ローディング、レスポンシブ以外にも、認証や共通ユーティリティなど必要に応じて追加してください。
- Docker と Docker Compose を使用して、フロントエンド、バックエンド、DynamoDB Local を一度に起動する。
- ローカルでフロントエンドのコードを変更したら、docker-compose up --build　をしなくてもブラウザをリロードすると反映されるようにする

---
