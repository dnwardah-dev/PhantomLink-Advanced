import { test, expect } from "@playwright/test";

test("Evidence Traceability panel displays expandable evidence", async ({ page }) => {
  const url = "https://paypal-login.example.com";

  await page.route("**/api/investigate/v2", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        engine: "PHANTOMLINK_V2_PIPELINE",
        status: "analyzed",
        hostname: "paypal-login.example.com",
        network_requests_performed: false,
        is_phishing_verdict: false,
        interpretation: {
          category: "ADDITIONAL_REVIEW",
          message: "Further investigation is required.",
          structural_signals: [],
          domain_signals: [],
          is_phishing_verdict: false,
          is_probability: false,
        },
        evidence_trace: [
          {
            evidence_id: "EV-structural-001",
            source: "structural",
            signal_code: "HOSTNAME_CONTAINS_HYPHEN",
            observed_evidence: "Hostname mengandung tanda hubung.",
            confidence: "LOW",
            explanation: "A structural characteristic was observed.",
            limitation: "This observation alone does not prove phishing.",
            is_phishing_verdict: false,
          },
          {
            evidence_id: "EV-domain-002",
            source: "domain",
            signal_code: "BRAND_AUTH_CONTEXT",
            observed_evidence: "Brand and authentication context detected.",
            confidence: "MEDIUM",
            explanation: "Brand context requires additional review.",
            limitation: "This observation alone does not prove phishing.",
            is_phishing_verdict: false,
          },
        ],
      }),
    });
  });

  await page.route("**/api/investigate", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        url,
        hostname: "paypal-login.example.com",
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

  await page
    .getByRole("textbox", { name: "Suspicious URL" })
    .fill(url);

  await page
    .getByRole("button", { name: "INITIATE INVESTIGATION" })
    .click();

  const panel = page.getByRole("region", {
    name: "Evidence Traceability",
  });

  await expect(panel).toBeVisible();
  await expect(panel).toContainText("2 EVIDENCE RECORDS");

  const hyphen = panel.getByRole("button", {
    name: /HOSTNAME_CONTAINS_HYPHEN/,
  });

  const brand = panel.getByRole("button", {
    name: /BRAND_AUTH_CONTEXT/,
  });

  await expect(hyphen).toHaveAttribute("aria-expanded", "false");

  await hyphen.click();

  await expect(hyphen).toHaveAttribute("aria-expanded", "true");
  await expect(panel).toContainText("EV-structural-001");
  await expect(panel).toContainText("Hostname mengandung tanda hubung.");
  await expect(panel).toContainText(
    "This observation alone does not prove phishing."
  );

  await brand.click();

  await expect(brand).toHaveAttribute("aria-expanded", "true");
  await expect(hyphen).toHaveAttribute("aria-expanded", "false");
  await expect(panel).toContainText("EV-domain-002");
  await expect(panel).toContainText("MEDIUM");

  await brand.click();

  await expect(brand).toHaveAttribute("aria-expanded", "false");
});
