import react from '@vitejs/plugin-react';
import { defineConfig, loadEnv } from 'vite';
import path from 'path';

export default defineConfig(({ command, mode }) => {
  // Load env file from frontend directory specifically
  const env = loadEnv(mode, path.resolve(__dirname), '');
  
  console.log('📋 Vite loaded env vars:', Object.keys(env).filter(k => k.startsWith('VITE_')));
  console.log('📂 Loading from directory:', path.resolve(__dirname));
  
  // Debug: show actual values being loaded
  console.log('✅ Loaded values:');
  console.log('  VITE_FIREBASE_API_KEY:', env.VITE_FIREBASE_API_KEY ? 'YES' : 'MISSING');
  console.log('  VITE_FIREBASE_AUTH_DOMAIN:', env.VITE_FIREBASE_AUTH_DOMAIN || 'MISSING');
  console.log('  VITE_FIREBASE_PROJECT_ID:', env.VITE_FIREBASE_PROJECT_ID || 'MISSING');

  return {
    plugins: [react()],
    define: {
      // Directly inject env vars into global scope so import.meta.env works
      'import.meta.env.VITE_FIREBASE_API_KEY': JSON.stringify(env.VITE_FIREBASE_API_KEY || ''),
      'import.meta.env.VITE_FIREBASE_AUTH_DOMAIN': JSON.stringify(env.VITE_FIREBASE_AUTH_DOMAIN || ''),
      'import.meta.env.VITE_FIREBASE_PROJECT_ID': JSON.stringify(env.VITE_FIREBASE_PROJECT_ID || ''),
      'import.meta.env.VITE_FIREBASE_STORAGE_BUCKET': JSON.stringify(env.VITE_FIREBASE_STORAGE_BUCKET || ''),
      'import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID': JSON.stringify(env.VITE_FIREBASE_MESSAGING_SENDER_ID || ''),
      'import.meta.env.VITE_FIREBASE_APP_ID': JSON.stringify(env.VITE_FIREBASE_APP_ID || ''),
      'import.meta.env.VITE_API_BASE_URL': JSON.stringify(env.VITE_API_BASE_URL || ''),
    },
    server: {
      port: 3000,
      proxy: {
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },
    build: {
      outDir: 'dist',
      sourcemap: true
    }
  };
});
