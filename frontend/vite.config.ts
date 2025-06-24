import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";
import {screenGraphPlugin} from "@animaapp/vite-plugin-screen-graph";

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  return {
    plugins: [react(), ...(mode === "development" ? [screenGraphPlugin()] : [])],
    publicDir: "./static",
    base: "/",
    resolve: {
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: process.env.VITE_BACKEND || 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
        }
      }
    }
  };
});