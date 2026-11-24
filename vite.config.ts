import path from "path"
import react from "@vitejs/plugin-react"
import { defineConfig } from "vite"

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    rollupOptions: {
      input: {
        main: path.resolve(__dirname, './index.html'),
        releaseDate: path.resolve(__dirname, './release-date/index.html'),
        pcSpecs: path.resolve(__dirname, './pc-specs/index.html'),
        xboxExecutable: path.resolve(__dirname, './news/xbox-executable/index.html'),
      },
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
});
