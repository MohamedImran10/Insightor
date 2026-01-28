import { defineConfig } from 'vite';

export default defineConfig({
  esbuild: {
    jsxInject: `import React from 'react'`,
    loader: 'jsx',
    include: /src\/.*\.jsx?$/,
  },
  server: {
    port: 3000,
  },
  build: {
    outDir: 'dist',
  },
});
