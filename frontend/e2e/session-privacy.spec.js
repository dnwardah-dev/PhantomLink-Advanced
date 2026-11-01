import { test, expect } from "@playwright/test";

const BASE = "http://127.0.0.1:5173";

test("investigation history is isolated between browser sessions", async ({
  browser,
}) => {
  const contextA = await browser.newContext();
  const contextB = await browser.newContext();

  try {
    const pageA = await contextA.newPage();
    const pageB = await contextB.newPage();

    await pageA.goto(`${BASE}/investigate`);
    await pageB.goto(`${BASE}/investigate`);

    const uniqueUrl =
      `https://case-${Date.now()}-a.example.com`;

    const investigationResponse = pageA.waitForResponse(
      (response) =>
        new URL(response.url()).pathname === "/api/investigate" &&
        response.request().method() === "POST"
    );

    await pageA
      .getByRole("textbox", { name: "Suspicious URL" })
      .fill(uniqueUrl);

    await pageA
      .getByRole("button", { name: "INITIATE INVESTIGATION" })
      .click();

    const response = await investigationResponse;
    expect(response.status()).toBe(200);

    // Use the browser's cookies, just as the frontend does.
    const historyA = await pageA.evaluate(async () => {
      const response = await fetch("/api/history");
      return {
        status: response.status,
        data: response.ok ? await response.json() : null,
      };
    });

    expect(historyA.status).toBe(200);

    // A separate browser context must not inherit A's session.
    const historyB = await pageB.evaluate(async () => {
      const response = await fetch("/api/history");
      return {
        status: response.status,
        data: response.ok ? await response.json() : null,
      };
    });

    expect(historyB.status).toBe(401);

    // Compare the actual browser cookie jars as well.
    const cookiesA = await contextA.cookies();
    const cookiesB = await contextB.cookies();

    expect(
      cookiesA.some((cookie) => cookie.name === "phantomlink_session")
    ).toBe(true);

    expect(
      cookiesB.some((cookie) => cookie.name === "phantomlink_session")
    ).toBe(false);
  } finally {
    await contextA.close();
    await contextB.close();
  }
});
