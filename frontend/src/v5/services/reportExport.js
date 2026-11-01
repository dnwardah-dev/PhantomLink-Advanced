function safeFilename(value) {
  return String(value || "unknown")
    .replace(/[^a-zA-Z0-9.-]/g, "_")
    .slice(0, 80);
}

export function exportInvestigationJSON(result) {
  if (!result || !result.investigation) {
    throw new Error("No investigation data to export.");
  }

  const investigation = result.investigation;
  const risk = result.risk_assessment ?? {};
  const evidence = Array.isArray(result.evidence)
    ? result.evidence
    : [];

  let hostname = "unknown";

  try {
    hostname = new URL(investigation.url).hostname;
  } catch {
    // Keep fallback
  }

  const report = {
    report_title: "PhantomLink Investigation Report",
    report_version: "1.0",
    generated_at: new Date().toISOString(),

    investigation: {
      id: investigation.id ?? null,
      hostname,
      url: investigation.url ?? null,
      timestamp: investigation.timestamp ?? null,
      analysis_type: investigation.analysis_type ?? "offline_heuristic",
    },

    risk_assessment: {
      score: risk.score ?? null,
      level: risk.level ?? "UNKNOWN",
      summary: risk.summary ?? "",
    },

    evidence: evidence.map((item) => ({
      code: item.code ?? "UNKNOWN",
      points: item.points ?? 0,
      explanation: item.explanation ?? "",
    })),

    recommendation: result.recommendation ?? "",
    disclaimer:
      result.disclaimer ??
      "This report is based on offline URL heuristics. It does not verify website safety.",
  };

  const filename = `PhantomLink_Case_${safeFilename(
    investigation.id
  )}_${safeFilename(hostname)}.json`;

  const blob = new Blob(
    [JSON.stringify(report, null, 2)],
    { type: "application/json;charset=utf-8" }
  );

  const downloadUrl = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = downloadUrl;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.setTimeout(() => {
    URL.revokeObjectURL(downloadUrl);
  }, 1000);
}
