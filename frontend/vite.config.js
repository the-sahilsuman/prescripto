import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')

  return {
    plugins: [
      react(),
      tailwindcss(),
    ],

    server: {
      host: true,

      // Do not automatically change the port
      strictPort: true,

      // Read port from .env
      port: Number(env.VITE_PORT) || 5173,

      // Allow your frontend URL
      allowedHosts: env.VITE_FRONTEND_URL
        ? [env.VITE_FRONTEND_URL]
        : [],
    },
  }
})