import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig(({ command }) => ({
  // Base path - use '/survey-ai/' for production, '/' for development
  base: command === 'serve' ? '/' : '/survey-ai/',
  
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      '/api/ai': {
        target: 'http://127.0.0.1:8002',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ai/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
}));
