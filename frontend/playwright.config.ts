import { defineConfig } from "@playwright/test";
export default defineConfig({
  use: {
    browserName: "chromium",
    headless: true,
    launchOptions: { args: ["--no-sandbox", "--disable-setuid-sandbox"] },
  },
  testDir: "./e2e",
});
