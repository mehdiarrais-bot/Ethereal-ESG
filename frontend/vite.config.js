import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    // changeOrigin: false garde le Host du navigateur (localhost:5173) : le
    // backend compare l'origine à l'hôte, port compris. La forme courte
    // (cible en simple chaîne) l'activerait et ferait refuser toute écriture.
    proxy: {
      '/api': { target: 'http://localhost:8000', changeOrigin: false },
      '/health': { target: 'http://localhost:8000', changeOrigin: false },
    }
  },
  build: {
    outDir: 'dist'
  }
})
