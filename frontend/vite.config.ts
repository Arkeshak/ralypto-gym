import tailwindcss from "@tailwindcss/vite";
import react from "@vitejs/plugin-react";
import { VitePWA } from "vite-plugin-pwa";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
    VitePWA({
      registerType: "autoUpdate",
      includeAssets: ["icons/brand.png"],
      manifest: {
        name: "Ralypto Gym",
        short_name: "Ralypto",
        description: "A clearer way to run your gym and keep members moving.",
        theme_color: "#11120f",
        background_color: "#11120f",
        display: "standalone",
        start_url: "/app/dashboard",
        scope: "/",
        categories: ["health", "fitness", "lifestyle"],
        icons: [
          {
            src: "/icons/brand.png",
            sizes: "1024x1024",
            type: "image/png",
            purpose: "any maskable",
          },
        ],
      },
    }),
  ],
  test: {
    environment: "jsdom",
    setupFiles: ["./src/test/setup.ts"],
    css: true,
  },
});
