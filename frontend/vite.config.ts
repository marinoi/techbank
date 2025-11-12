import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: "0.0.0.0",
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://nginx:80',
        changeOrigin: true,
        secure: false,
      }
    }
    
    /* {
      '/api/auth': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
      },
      '/api/wallet': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        secure: false,
      },
      '/api/card': {
        target: 'http://localhost:8002',
        changeOrigin: true,
        secure: false,
      },
      '/api/notification': {
        target: 'http://localhost:8003',
        changeOrigin: true,
        secure: false,
      },
    } */

  },
})
