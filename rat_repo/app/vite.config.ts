import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173,
    allowedHosts: [
      "location-dome-developmental-practitioner.trycloudflare.com",
      "mental-maintain-measures-hitachi.trycloudflare.com"
    ]
  }
});
