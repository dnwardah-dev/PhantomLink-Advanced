import { test, expect } from "@playwright/test";

const BASE = "http://127.0.0.1:5173";

test("two active sessions cannot access each other's investigations", async ({
  browser,
}) => {
  const contextA = await browser.newContext();
  const contextB = await browser.newContext();

  try {
    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();

    await pageA.goto(`${BASE}/investigate`);
    await pageB.goto(`${BASE}/investigate`);

    const unique = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;

    const urlA = `https://case-${unique}-a.example.com`;
    const urlB = `https://case-${unique}-b.example.com`;

    async function investigate(page, url) {
      const responsePromise = page.waitForResponse(
        (response) =>
          new URL(response.url()).pathname === "/api/investigate" &&
          response.request().method() === "POST"
      );

      await page
        .getByRole("textbox", { name: "Suspicious URL" })
        .fill(url);

      await page
        .getByRole("button", { name: "INITIATE INVESTIGATION" })
        .click();

      const response = await responsePromise;
      expect(response.status()).toBe(200);
    }

    await investigate(pageA, urlA);
    await investigate(pageB, urlB);

    async function readHistory(page) {
      return page.evaluate(async () => {
        const response = await fetch("/api/history");

        return {
          status: response.status,
          data: await response.json(),
        };
      });
    }

    const historyA = await readHistory(pageA);
    const historyB = await readHistory(pageB);

    expect(historyA.status).toBe(200);
    expect(historyB.status).toBe(200);

    // Compare server-returned investigation records.
    // The backend stores hostnames, not full URLs.
    const recordsA = JSON.stringify(historyA.data);
    const recordsB = JSON.stringify(historyB.data);

    const hostnameA = new URL(urlA).hostname;
    const hostnameB = new URL(urlB).hostname;

    expect(recordsA).toContain(hostnameA);
    expect(recordsA).not.toContain(hostnameB);

    expect(recordsB).toContain(hostnameB);
    expect(recordsB).not.toContain(hostnameA);

    const cookiesA = await contextA.cookies();
    const cookiesB = await contextB.cookies();

    const tokenA = cookiesA.find(
      (cookie) => cookie.name === "phantomlink_session"
    );

    const tokenB = cookiesB.find(
      (cookie) => cookie.name === "phantomlink_session"
    );

    expect(tokenA).toBeDefined();
    expect(tokenB).toBeDefined();
    expect(tokenA.value).not.toBe(tokenB.value);
  } finally {
    await contextA.close();
    await contextB.close();
  }
});
