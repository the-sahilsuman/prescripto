import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server:{
    host: true,
    strictPort: true,
    port: process.env.PORT,
    allowedHosts: [process.env.VITE_FRONTEND_URL]
}
})
