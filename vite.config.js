import { defineConfig } from 'vite'
import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    tailwindcss(),
    react()
  ],
  
  // Set the base for relative paths (important for Electron)
  base: './',
  
  // Build optimizations
  build: {
    target: 'esnext',
    minify: 'esbuild',
    outDir: 'dist',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          utils: ['axios', 'lucide-react']
        }
      }
    }
  },
  
  // Development server configuration
  server: {
    port: 5173,
    host: true,
    cors: true
  },
  
  // Preview server configuration
  preview: {
    port: 4173,
    host: true
  },
  
  // ESBuild configuration to handle JSX in .js files if needed
  esbuild: {
    loader: 'jsx',
    include: /src\/.*\.[jt]sx?$/,
    exclude: []
  }
})
