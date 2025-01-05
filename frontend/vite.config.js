import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ["**/*.md"],
  server: {
    proxy: {
      "/p/": {target: "http://51.20.96.129/"},
      "/api": {
        target: "https://nyrk.io",
        // target: "http://localhost",
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
