import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  assetsInclude: ["**/*.md"],
  publicDir: "public",
  server: {
    proxy: {
      "/p/": {target: "http://localhost/"},
      //"/p/": {target: "http://nyrkio.com/"},
      "/api": {
        target: "https://nyrkio.com",
        //target: "https://staging.nyrkio.com",
        // target: "http://localhost:8001",
        changeOrigin: true,
        // rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
