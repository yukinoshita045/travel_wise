import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      // 開發模式下將 /api 請求代理到後端，避免 CORS 問題
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true,
      },
    },
  },
})