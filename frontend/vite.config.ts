import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,          // listen on 0.0.0.0 so Docker can expose it
    port: 3000,
    watch: {
      usePolling: true,  // required for file-watching inside Docker volumes
    },
    proxy: {
      '/auth':     { target: 'http://api:8000', changeOrigin: true },
      '/upload':   { target: 'http://api:8000', changeOrigin: true },
      '/pipeline': { target: 'http://api:8000', changeOrigin: true },
      '/health':   { target: 'http://api:8000', changeOrigin: true },
    },
  },
})
