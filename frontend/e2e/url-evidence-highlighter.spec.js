import { test, expect } from "@playwright/test";

test("URL Evidence Explorer highlights mapped characters", async ({ page }) => {
  const url = "https://school-portal-2026.example.com";
  const hostname = "school-portal-2026.example.com";

  const makeMapping = (code, char) => ({
    evidence_id: `EV-${code}`,
    signal_code: code,
    component: "hostname",
    component_value: hostname,
    spans: [...hostname].flatMap((value, index) =>
      char(value)
        ? [{ start: index, end: index + 1 }]
        : []
    ),
    mapping_type: "DIRECT_CHARACTER_MATCH",
    is_phishing_verdict: false,
  });

  await page.route("**/api/investigate/v2", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        engine: "PHANTOMLINK_V2_PIPELINE",
        status: "analyzed",
        hostname,
        normalized_url: url,
        network_requests_performed: false,
        is_phishing_verdict: false,
        interpretation: {
          category: "STRUCTURAL_OBSERVATION",
          message: "Structural characteristics observed.",
          structural_signals: [],
          domain_signals: [],
          is_phishing_verdict: false,
          is_probability: false,
        },
        evidence_trace: [],
        url_evidence_map: [
          makeMapping(
            "HOSTNAME_CONTAINS_HYPHEN",
            (char) => char === "-"
          ),
          makeMapping(
            "HOSTNAME_CONTAINS_DIGITS",
            (char) => /[0-9]/.test(char)
          ),
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
        hostname,
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
    name: "URL Evidence Highlighter",
  });

  await expect(panel).toBeVisible();
  await expect(panel).toContainText("2 MAPPINGS");

  const highlighted = panel.locator(
    ".v5-url-map-character.is-highlighted"
  );

  const hyphen = panel.getByRole("button", {
    name: "HOSTNAME_CONTAINS_HYPHEN",
  });

  const digits = panel.getByRole("button", {
    name: "HOSTNAME_CONTAINS_DIGITS",
  });

  await expect(highlighted).toHaveCount(0);

  await hyphen.click();
  await expect(hyphen).toHaveAttribute("aria-pressed", "true");
  await expect(highlighted).toHaveCount(2);
  await expect(highlighted).toHaveText(["-", "-"]);

  await digits.click();
  await expect(hyphen).toHaveAttribute("aria-pressed", "false");
  await expect(digits).toHaveAttribute("aria-pressed", "true");
  await expect(highlighted).toHaveCount(4);
  await expect(highlighted).toHaveText(["2", "0", "2", "6"]);

  await digits.click();
  await expect(digits).toHaveAttribute("aria-pressed", "false");
  await expect(highlighted).toHaveCount(0);
});
