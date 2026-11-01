import { jsPDF } from "jspdf";

const C = {
  bg: [8, 12, 25],
  panel: [20, 28, 49],
  cyan: [101, 232, 244],
  purple: [173, 145, 255],
  white: [242, 246, 255],
  muted: [165, 179, 205],
  green: [110, 231, 183],
  yellow: [255, 191, 105],
  red: [255, 113, 140],
};

export function exportInvestigationPDF(result) {
  if (!result?.investigation) {
    throw new Error("No investigation data to export.");
  }

  const investigation = result.investigation;
  const risk = result.risk_assessment ?? {};
  const evidence = Array.isArray(result.evidence)
    ? result.evidence
    : [];

  const doc = new jsPDF({
    orientation: "portrait",
    unit: "mm",
    format: "a4",
  });

  const W = 210;
  const H = 297;
  const M = 18;
  const CW = W - M * 2;
  const bottomLimit = 266;

  let y = 0;
  let page = 0;

  function fill(color) {
    doc.setFillColor(...color);
  }

  function textColor(color) {
    doc.setTextColor(...color);
  }

  function newPage() {
    if (page > 0) doc.addPage();
    page++;

    fill(C.bg);
    doc.rect(0, 0, W, H, "F");

    fill(C.purple);
    doc.rect(0, 0, 3, H, "F");

    textColor(C.cyan);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(16);
    doc.text("PHANTOMLINK", M, 20);

    textColor(C.muted);
    doc.setFontSize(8);
    doc.text("DIGITAL THREAT INTELLIGENCE", M, 27);

    doc.setDrawColor(...C.panel);
    doc.line(M, 33, W - M, 33);

    y = 44;
  }

  function checkPage(height = 15) {
    if (y + height > bottomLimit) newPage();
  }

  function sectionTitle(number, title) {
    checkPage(18);
    y += 5;

    textColor(C.cyan);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(9);
    doc.text(`${number} / ${title}`, M, y);

    y += 9;
  }

  function paragraph(value, color = C.muted) {
    const content = String(value ?? "Not available");

    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);

    const lines = doc.splitTextToSize(content, CW - 5);

    textColor(color);

    for (const line of lines) {
      checkPage(6);
      doc.text(line, M, y);
      y += 5.5;
    }

    y += 5;
  }

  function field(label, value) {
    checkPage(16);

    textColor(C.muted);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(8);
    doc.text(label, M, y);

    y += 6;

    paragraph(String(value ?? "N/A"), C.white);
  }

  function evidenceCard(item, index) {
    const code = String(item.code ?? "UNKNOWN");
    const explanation = String(
      item.explanation ?? "No explanation provided."
    );

    const lines = doc.splitTextToSize(explanation, CW - 16);
    const cardHeight = Math.max(27, 20 + lines.length * 5);

    checkPage(cardHeight + 5);

    fill(C.panel);
    doc.roundedRect(M, y, CW, cardHeight, 3, 3, "F");

    textColor(C.white);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(10);
    doc.text(`${index + 1}. ${code}`, M + 7, y + 9);

    textColor(C.yellow);
    doc.setFontSize(9);
    doc.text(
      `+${item.points ?? 0} RISK POINTS`,
      W - M - 7,
      y + 9,
      { align: "right" }
    );

    textColor(C.muted);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.text(lines, M + 7, y + 18);

    y += cardHeight + 5;
  }

  let hostname = "unknown";

  try {
    hostname = new URL(investigation.url).hostname;
  } catch {
    // Retain fallback
  }

  const score = Number.isFinite(Number(risk.score))
    ? Math.max(0, Math.min(100, Number(risk.score)))
    : null;

  const level = String(risk.level ?? "UNKNOWN").toUpperCase();

  const levelColor =
    level === "HIGH" || level === "CRITICAL"
      ? C.red
      : level === "MEDIUM"
        ? C.yellow
        : level === "LOW"
          ? C.green
          : C.muted;

  newPage();

  textColor(C.white);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(21);
  doc.text("URL INVESTIGATION REPORT", M, y);
  y += 11;

  field("CASE ID", investigation.id ?? "N/A");
  field("TARGET HOSTNAME", hostname);
  field("TARGET URL", investigation.url ?? "N/A");
  field("INVESTIGATION TIMESTAMP", investigation.timestamp ?? "N/A");

  checkPage(43);

  fill(C.panel);
  doc.roundedRect(M, y, CW, 38, 4, 4, "F");

  textColor(C.muted);
  doc.setFont("helvetica", "bold");
  doc.setFontSize(9);
  doc.text("RISK SCORE", M + 10, y + 10);
  doc.text("CLASSIFICATION", M + 100, y + 10);

  textColor(C.white);
  doc.setFontSize(24);
  doc.text(
    score === null ? "N/A" : `${score}/100`,
    M + 10,
    y + 27
  );

  textColor(levelColor);
  doc.setFontSize(19);
  doc.text(level, M + 100, y + 27);

  y += 45;

  sectionTitle("01", "EXECUTIVE SUMMARY");
  paragraph(risk.summary ?? "No summary available.");

  // Keep the evidence section together when it fits on one page.
  const evidenceHeight = evidence.reduce((total, item) => {
    const explanation = String(
      item.explanation ?? "No explanation provided."
    );

    const lines = doc.splitTextToSize(explanation, CW - 16);
    const cardHeight = Math.max(27, 20 + lines.length * 5);

    return total + cardHeight + 5;
  }, 0);

  if (
    evidence.length > 0 &&
    evidenceHeight + 23 <= bottomLimit - 44 &&
    y + evidenceHeight + 23 > bottomLimit
  ) {
    newPage();
  }

  sectionTitle("02", "DETECTED EVIDENCE");

  if (evidence.length === 0) {
    paragraph("No suspicious indicators were reported.");
  } else {
    evidence.forEach(evidenceCard);
  }

  sectionTitle("03", "THREAT INTELLIGENCE ANALYSIS");

  const explanations = Array.isArray(result.threat_explanations)
    ? result.threat_explanations
    : [];

  if (explanations.length === 0) {
    paragraph("No detailed threat explanations available.");
  } else {
    explanations.forEach((item, index) => {
      checkPage(22);

      textColor(C.purple);
      doc.setFont("helvetica", "bold");
      doc.setFontSize(10);

      const title = `${index + 1}. ${item.title || item.code || "Indicator"}`;
      const titleLines = doc.splitTextToSize(title, CW);

      for (const line of titleLines) {
        checkPage(6);
        doc.text(line, M, y);
        y += 6;
      }

      paragraph(item.reason || "No explanation available.");
      paragraph(`Precaution: ${item.action || "Verify the URL independently."}`);
    });
  }

  sectionTitle("04", "SECURITY RECOMMENDATION");
  paragraph(result.recommendation ?? "No recommendation provided.");

  sectionTitle("05", "ANALYSIS LIMITATIONS");
  paragraph(
    result.disclaimer ??
    "This report is based on offline URL heuristics. " +
    "No website content, redirect chain, or live network traffic was analyzed."
  );

  for (let i = 1; i <= doc.getNumberOfPages(); i++) {
    doc.setPage(i);

    doc.setDrawColor(...C.panel);
    doc.line(M, 278, W - M, 278);

    textColor(C.muted);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);

    doc.text("PHANTOMLINK / FORENSIC INVESTIGATION", M, 286);

    doc.text(
      `PAGE ${String(i).padStart(2, "0")} / ${String(
        doc.getNumberOfPages()
      ).padStart(2, "0")}`,
      W - M,
      286,
      { align: "right" }
    );
  }

  const safeId = String(investigation.id ?? "unknown")
    .replace(/[^a-zA-Z0-9_-]/g, "_")
    .slice(0, 40);

  doc.save(`PhantomLink_Case_${safeId}_Report.pdf`);
}
