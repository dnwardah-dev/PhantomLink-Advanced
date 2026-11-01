/* @vitest-environment jsdom */

import React from "react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { act, cleanup, render, screen } from "@testing-library/react";

import {
  InvestigationProvider,
  useInvestigation,
} from "../InvestigationContext";

import {
  investigateURL,
  investigateURLV2,
  inspectDNS,
} from "../../services/api";

vi.mock("../../services/api", () => ({
  investigateURL: vi.fn(),
  investigateURLV2: vi.fn(),
  inspectDNS: vi.fn(),
}));

function deferred() {
  let resolve;
  let reject;

  const promise = new Promise((res, rej) => {
    resolve = res;
    reject = rej;
  });

  return { promise, resolve, reject };
}

let context;

function Probe() {
  context = useInvestigation();

  return (
    <div>
      <output data-testid="v1">
        {context.result?.marker ?? "none"}
      </output>
      <output data-testid="v2">
        {context.v2Result?.marker ?? "none"}
      </output>
      <output data-testid="dns">
        {context.dnsData?.marker ?? "none"}
      </output>
      <output data-testid="v2-error">
        {context.v2Error || "none"}
      </output>
      <output data-testid="dns-error">
        {context.dnsError || "none"}
      </output>
    </div>
  );
}

async function flush() {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

afterEach(() => {
  cleanup();
  vi.resetAllMocks();
  context = undefined;
});

describe("InvestigationContext race conditions", () => {
  it("ignores late responses from an older investigation", async () => {
    const oldV1 = deferred();
    const newV1 = deferred();

    investigateURL
      .mockReturnValueOnce(oldV1.promise)
      .mockReturnValueOnce(newV1.promise);

    investigateURLV2.mockImplementation(async (url) => ({
      marker: url,
    }));

    inspectDNS.mockImplementation(async (url) => ({
      marker: url,
    }));

    render(
      <InvestigationProvider>
        <Probe />
      </InvestigationProvider>
    );

    await act(async () => {
      void context.runInvestigation("https://old.example");
      void context.runInvestigation("https://new.example");
    });

    await act(async () => {
      newV1.resolve({ marker: "NEW" });
    });

    await flush();

    expect(screen.getByTestId("v1").textContent).toBe("NEW");
    expect(screen.getByTestId("v2").textContent).toBe(
      "https://new.example"
    );
    expect(screen.getByTestId("dns").textContent).toBe(
      "https://new.example"
    );

    await act(async () => {
      oldV1.resolve({ marker: "OLD" });
    });

    await flush();

    expect(screen.getByTestId("v1").textContent).toBe("NEW");
    expect(screen.getByTestId("v2").textContent).toBe(
      "https://new.example"
    );
  });

  it("keeps V1 result when V2 fails", async () => {
    investigateURL.mockResolvedValue({ marker: "V1_OK" });
    investigateURLV2.mockRejectedValue(
      new Error("V2 temporarily unavailable")
    );
    inspectDNS.mockResolvedValue({ marker: "DNS_OK" });

    render(
      <InvestigationProvider>
        <Probe />
      </InvestigationProvider>
    );

    await act(async () => {
      await context.runInvestigation("https://example.com");
    });

    await flush();

    expect(screen.getByTestId("v1").textContent).toBe("V1_OK");
    expect(screen.getByTestId("dns").textContent).toBe("DNS_OK");
    expect(screen.getByTestId("v2-error").textContent).toContain(
      "V2 temporarily unavailable"
    );
  });

  it("keeps V1 and V2 when DNS fails", async () => {
    investigateURL.mockResolvedValue({ marker: "V1_OK" });
    investigateURLV2.mockResolvedValue({ marker: "V2_OK" });
    inspectDNS.mockRejectedValue(new Error("DNS lookup failed"));

    render(
      <InvestigationProvider>
        <Probe />
      </InvestigationProvider>
    );

    await act(async () => {
      await context.runInvestigation("https://example.com");
    });

    await flush();

    expect(screen.getByTestId("v1").textContent).toBe("V1_OK");
    expect(screen.getByTestId("v2").textContent).toBe("V2_OK");
    expect(screen.getByTestId("dns-error").textContent).toContain(
      "DNS lookup failed"
    );
  });
});

describe("InvestigationContext advanced race conditions", () => {
  it("ignores late DNS and V2 responses after a new scan", async () => {
    const oldDNS = deferred();
    const oldV2 = deferred();

    investigateURL.mockImplementation(async (url) => ({
      marker: url,
    }));

    inspectDNS.mockImplementation((url) =>
      url === "https://old.example"
        ? oldDNS.promise
        : Promise.resolve({ marker: "NEW_DNS" })
    );

    investigateURLV2.mockImplementation((url) =>
      url === "https://old.example"
        ? oldV2.promise
        : Promise.resolve({ marker: "NEW_V2" })
    );

    render(
      <InvestigationProvider>
        <Probe />
      </InvestigationProvider>
    );

    // First investigation: V1 finishes, DNS and V2 remain pending.
    await act(async () => {
      await context.runInvestigation("https://old.example");
    });

    expect(screen.getByTestId("v1").textContent).toBe(
      "https://old.example"
    );

    expect(inspectDNS).toHaveBeenCalledWith("https://old.example");
    expect(investigateURLV2).toHaveBeenCalledWith(
      "https://old.example"
    );

    // Second investigation finishes, including its supplementary data.
    await act(async () => {
      await context.runInvestigation("https://new.example");
    });

    await flush();

    expect(screen.getByTestId("v1").textContent).toBe(
      "https://new.example"
    );
    expect(screen.getByTestId("dns").textContent).toBe("NEW_DNS");
    expect(screen.getByTestId("v2").textContent).toBe("NEW_V2");

    // Old responses arrive after the new investigation.
    await act(async () => {
      oldDNS.resolve({ marker: "OLD_DNS" });
      oldV2.resolve({ marker: "OLD_V2" });
    });

    await flush();

    // None of the old responses may overwrite the newest state.
    expect(screen.getByTestId("v1").textContent).toBe(
      "https://new.example"
    );
    expect(screen.getByTestId("dns").textContent).toBe("NEW_DNS");
    expect(screen.getByTestId("v2").textContent).toBe("NEW_V2");
    expect(screen.getByTestId("dns-error").textContent).toBe("none");
    expect(screen.getByTestId("v2-error").textContent).toBe("none");
  });
});

describe("InvestigationContext stale error protection", () => {
  it("ignores stale DNS and V2 errors after a new scan", async () => {
    const oldDNS = deferred();
    const oldV2 = deferred();

    investigateURL.mockImplementation(async (url) => ({
      marker: url,
    }));

    inspectDNS.mockImplementation((url) =>
      url === "https://old.example"
        ? oldDNS.promise
        : Promise.resolve({ marker: "NEW_DNS" })
    );

    investigateURLV2.mockImplementation((url) =>
      url === "https://old.example"
        ? oldV2.promise
        : Promise.resolve({ marker: "NEW_V2" })
    );

    render(
      <InvestigationProvider>
        <Probe />
      </InvestigationProvider>
    );

    await act(async () => {
      await context.runInvestigation("https://old.example");
    });

    await act(async () => {
      await context.runInvestigation("https://new.example");
    });

    await flush();

    expect(screen.getByTestId("v1").textContent).toBe(
      "https://new.example"
    );

    expect(screen.getByTestId("dns").textContent).toBe("NEW_DNS");
    expect(screen.getByTestId("v2").textContent).toBe("NEW_V2");

    // Old requests fail AFTER the new investigation succeeds.
    await act(async () => {
      oldDNS.reject(new Error("OLD_DNS_ERROR"));
      oldV2.reject(new Error("OLD_V2_ERROR"));
    });

    await flush();

    // Errors from old requests must not contaminate new results.
    expect(screen.getByTestId("dns-error").textContent).toBe("none");
    expect(screen.getByTestId("v2-error").textContent).toBe("none");

    expect(screen.getByTestId("dns").textContent).toBe("NEW_DNS");
    expect(screen.getByTestId("v2").textContent).toBe("NEW_V2");
  });
});
