import { test, expect } from "@playwright/test";

const routes = [
  "/",
  "/investigate",
  "/evidence",
  "/dns",
  "/archive",
  "/analytics",
];

for (const route of routes) {
  test(`route ${route} renders after lazy loading`, async ({ page }) => {
    const errors = [];

    page.on("pageerror", (error) => {
      errors.push(error.message);
    });

    const response = await page.goto(
      `http://127.0.0.1:5173${route}`
    );

    expect(response?.status()).toBe(200);

    await expect(page.locator("#root")).not.toBeEmpty();

    await expect(
      page.getByText("Loading PhantomLink...")
    ).toBeHidden({ timeout: 15000 });

    await expect(page.locator("main.v5-platform-main")).toBeVisible({
      timeout: 15000,
    });

    expect(errors).toEqual([]);
  });
}

