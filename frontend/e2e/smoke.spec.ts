import { test, expect } from "@playwright/test";

test("smoke all buttons + populated data", async ({ page }) => {
  await page.goto("http://localhost:5173/");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1")).toContainText(/Übersicht|Overview/);

  await page.goto("http://localhost:5173/diagnostics");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1")).toContainText(/Diagnostik|Diagnostics/);
  await page.getByRole("button", { name: /Simulation starten|Run simulation/ }).click();
  await page.waitForTimeout(2000);
  await expect(page.locator("table tbody tr").first()).toBeVisible({ timeout: 5000 });

  const filterSel = page.locator("select").nth(1);
  if (await filterSel.count()) {
    await filterSel.selectOption("block");
    await page.waitForTimeout(500);
  }

  await page.locator('input[placeholder*="Name"], input[placeholder*="name"]').first().fill("e2e-rule");
  await page.getByRole("button", { name: /Regel hinzufügen|Add rule/ }).click();
  await page.waitForTimeout(500);
  await expect(page.locator("text=e2e-rule")).toBeVisible();

  const togBtn = page.getByRole("button", { name: /Umschalten|Toggle/ }).first();
  if (await togBtn.count()) await togBtn.click();
  await page.waitForTimeout(300);
  const delBtn = page.getByRole("button", { name: /Löschen|Delete/ }).first();
  if (await delBtn.count()) await delBtn.click();
  await page.waitForTimeout(300);

  await page.locator("button.iconbtn").first().click();
  await page.waitForTimeout(200);

  await page.goto("http://localhost:5173/cache");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1")).toContainText(/Cache-Lab|Cache/);

  await page.goto("http://localhost:5173/reports");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1")).toContainText(/Berichte|Reports/);
  const dlBtn = page.getByRole("button", { name: /Bericht herunterladen|Download report/ });
  if (await dlBtn.count()) await dlBtn.click();
  await page.waitForTimeout(500);

  await page.goto("http://localhost:5173/about");
  await page.waitForLoadState("networkidle");
  await expect(page.locator("h1")).toContainText(/Über|About/);

  await page.locator("select").first().selectOption("en");
  await page.waitForTimeout(300);
  await expect(page.locator("h1").first()).toContainText(/Über|About|Overview|Diagnostics|Cache/);
  await page.locator("select").first().selectOption("de");
  await page.waitForTimeout(300);
});
