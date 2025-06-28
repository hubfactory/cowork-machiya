// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  srcDir: 'app/',
  compatibilityDate: '2025-05-15',
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@nuxt/icon',
    '@vueuse/nuxt',
  ],
  css: [
    // 必要に応じてグローバルSCSSファイルを追加
  ],
})
