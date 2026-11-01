import { test, expect } from "@playwright/test";

const cases = [
  {
    url: "https://example.com",
    category: "INSUFFICIENT EVIDENCE",
    backendCategory: "INSUFFICIENT_EVIDENCE",
    signals: [],
  },
  {
    url: "https://school-portal-2026.example.com",
    category: "STRUCTURAL OBSERVATION",
    backendCategory: "STRUCTURAL_OBSERVATION",
    signals: [
      {
        code: "HOSTNAME_CONTAINS_HYPHEN",
        evidence: "Hostname mengandung tanda hubung.",
        confidence: "LOW",
      },
    ],
  },
  {
    url: "https://paypal-login.example.com",
    category: "ADDITIONAL REVIEW",
    backendCategory: "ADDITIONAL_REVIEW",
    signals: [
      {
        code: "BRAND_AUTH_CONTEXT",
        evidence: "Brand and authentication language detected.",
        confidence: "MEDIUM",
      },
    ],
  },
];

test.describe("PhantomLink V2 browser integration", () => {
  for (const scenario of cases) {
    test(`displays ${scenario.category}`, async ({ page }) => {
      await page.route("**/api/investigate/v2", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            engine: "PHANTOMLINK_V2_PIPELINE",
            status: "analyzed",
            hostname: new URL(scenario.url).hostname,
            network_requests_performed: false,
            is_phishing_verdict: false,
            interpretation: {
              category: scenario.backendCategory,
              message: "Experimental evidence interpretation.",
              structural_signals: scenario.signals,
              domain_signals: [],
              is_probability: false,
              is_phishing_verdict: false,
            },
          }),
        });
      });

      // Mock V1 failure-free response while preserving the frontend flow.
      await page.route("**/api/investigate", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            url: scenario.url,
            hostname: new URL(scenario.url).hostname,
            risk_score: 0,
            risk_level: "LOW",
            indicators: [],
            explanations: [],
          }),
        });
      });

      await page.route("**/api/dns-intelligence", async (route) => {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ status: "ok", records: [] }),
        });
      });

      await page.goto("http://127.0.0.1:5173/investigate");

      const input = page.getByRole("textbox", { name: "Suspicious URL" });
      await expect(input).toBeVisible();

      await input.fill(scenario.url);

      // Submit through the actual UI.
      await page.getByRole("button", { name: "INITIATE INVESTIGATION" }).click();

      const panel = page.getByRole("region", {
        name: "V2 Evidence Intelligence",
      });

      await expect(panel).toBeVisible();
      await expect(panel).toContainText(scenario.category);

      for (const signal of scenario.signals) {
        await expect(panel).toContainText(signal.code);
      }
    });
  }
});

