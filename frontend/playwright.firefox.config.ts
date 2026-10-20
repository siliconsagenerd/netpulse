import { defineConfig } from "@playwright/test";
export default defineConfig({
  use: {
    browserName: "firefox",
    headless: true,
    launchOptions: { args: [] },
  },
  testDir: "./e2e",
});
