import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from "path" // Added path import

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"), // Added alias for @
    },
  },
})
