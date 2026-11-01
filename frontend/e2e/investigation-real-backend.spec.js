import { test, expect } from "@playwright/test";

test("real backend returns V2 evidence", async ({ page }) => {
  const v2Response = page.waitForResponse(
    (response) =>
      response.url().includes("/api/investigate/v2") &&
      response.request().method() === "POST"
  );

  await page.goto("http://127.0.0.1:5173/investigate");

  await page
    .getByRole("textbox", { name: "Suspicious URL" })
    .fill("https://paypal-login.example.com");

  await page
    .getByRole("button", { name: "INITIATE INVESTIGATION" })
    .click();

  const response = await v2Response;

  expect(response.status()).toBe(200);

  const data = await response.json();

  expect(data.engine).toBe("PHANTOMLINK_V2_PIPELINE");
  expect(data.interpretation.category).toBe("ADDITIONAL_REVIEW");
  expect(data.is_phishing_verdict).toBe(false);

  const panel = page.getByRole("region", {
    name: "V2 Evidence Intelligence",
  });

  await expect(panel).toBeVisible();
  await expect(panel).toContainText("ADDITIONAL REVIEW");
  await expect(panel).toContainText("BRAND_AUTH_CONTEXT");
});
