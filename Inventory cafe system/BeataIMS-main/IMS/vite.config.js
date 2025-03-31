// vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': '/src', // Make sure your path is correct
    },
  },
  server: {
    open: 'chrome', // Opens Chrome when starting the server
  },
});
