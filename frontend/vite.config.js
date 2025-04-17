import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // any request to /predict → http://localhost:8000/predict
      "/predict": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
      "/history": {
        target: "http://localhost:8000",
        changeOrigin: true,
        secure: false,
      },
    },
  },
});
