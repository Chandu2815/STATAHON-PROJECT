import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  // Base path for production deployment
  // When served under /survey-ai path, all assets and routes will be correctly resolved
  base: '/survey-ai/',
  
  plugins: [react()],
  server: {
    port: 5173,
    strictPort: false,
    proxy: {
      '/api/ai': {
        target: 'http://localhost:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/ai/, ''),
      },
    },
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
});
