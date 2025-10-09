import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Proxy API to backend during dev
const API_PROXY = 'http://localhost:8000'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: API_PROXY,
        changeOrigin: true,
      },
    },
  },
})
