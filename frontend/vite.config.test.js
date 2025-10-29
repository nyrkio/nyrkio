import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Local development configuration
// This config proxies API requests to a local backend server
// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ["**/*.md"],
  publicDir: "public",
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8001",
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
