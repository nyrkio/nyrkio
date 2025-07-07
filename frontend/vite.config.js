import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ["**/*.md"],
  publicDir: "public",
  server: {
    proxy: {
      // "/p/": {target: "http://51.20.96.129/"},
      "/api": {
        target: "https://nyrk.io",
        //target: "https://staging.nyrkio.com",
        // target: "http://localhost",
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
