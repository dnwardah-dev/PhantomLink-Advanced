const API_BASE = "/api";

async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    let message = `API request failed (${response.status})`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      }
    } catch {
      // Use default error message
    }

    throw new Error(message);
  }

  return response.json();
}

export async function investigateURL(url) {
  return apiRequest("/investigate", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

export async function getInvestigationHistory() {
  return apiRequest("/history");
}


export async function inspectDNS(url) {
  return apiRequest("/dns-intelligence", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}

// Experimental V2 investigation API.
// The existing V1 API remains unchanged.
export async function investigateURLV2(url) {
  return apiRequest("/investigate/v2", {
    method: "POST",
    body: JSON.stringify({ url }),
  });
}
