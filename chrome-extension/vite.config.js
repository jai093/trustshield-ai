import { defineConfig } from 'vite';
import { resolve } from 'node:path';

export default defineConfig({
  base: './',
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        popup: resolve(__dirname, 'popup.html'),
        options: resolve(__dirname, 'options.html'),
        background: resolve(__dirname, 'src/background.js'),
        'content-scripts/gmail': resolve(__dirname, 'src/content-scripts/gmail.js'),
        'content-scripts/outlook': resolve(__dirname, 'src/content-scripts/outlook.js')
      },
      output: {
        entryFileNames: (chunkInfo) => {
          if (chunkInfo.name === 'background') return 'background.js';
          if (chunkInfo.name === 'content-scripts/gmail') return 'content-scripts/gmail.js';
          if (chunkInfo.name === 'content-scripts/outlook') return 'content-scripts/outlook.js';
          return '[name].js';
        }
      }
    }
  }
});
