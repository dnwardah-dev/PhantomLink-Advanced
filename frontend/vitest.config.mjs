import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["src/**/*.{test,spec}.{js,jsx,ts,tsx}"],
    exclude: ["node_modules/**", "dist/**", "e2e/**"],
    environment: "jsdom",
  },
});
