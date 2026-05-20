import { defineConfig } from "vite";
import { createSvgIconsPlugin } from 'vite-plugin-svg-icons';
import path from 'path';
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [
    react(),
    createSvgIconsPlugin({
      iconDirs: [path.resolve(process.cwd(), 'src/assets/icons')],
      symbolId: 'icon-[name]',
    }),
  ],
  assetsInclude: ["**/*.md"],
  publicDir: "public",
  css: {
    preprocessorOptions: {
      scss: {
        silenceDeprecations: ["legacy-js-api", "import", "global-builtin", "color-functions", "if-function"],
      },
    },
  },
  server: {
    proxy: {
      "/p/": {target: "http://localhost/"},
      //"/p/": {target: "http://nyrkio.com/"},
      "/api": {
        target: process.env.VITE_API_TARGET || "http://localhost:8000",
        //target: "https://staging.nyrkio.com",
        // target: "http://localhost:8001",
        changeOrigin: true,
        secure: false,
        // rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
