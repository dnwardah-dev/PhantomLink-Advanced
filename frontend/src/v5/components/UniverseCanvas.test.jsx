import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import { render, screen, act, cleanup } from "@testing-library/react";
import { useState } from "react";
import UniverseCanvas from "./UniverseCanvas";

const mockCanvas = vi.hoisted(() => vi.fn());

vi.mock("@react-three/fiber", () => ({
  Canvas: (props) => {
    mockCanvas(props.frameloop);
    return <div data-testid="mock-canvas" />;
  },
}));

vi.mock("../../scenes/ThreatUniverse", () => ({
  default: () => null,
}));

describe("UniverseCanvas visibility optimization", () => {
  let hidden = false;

  beforeEach(() => {
    hidden = false;
    mockCanvas.mockClear();

    Object.defineProperty(document, "hidden", {
      configurable: true,
      get: () => hidden,
    });
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("uses always when the page is visible", () => {
    render(<UniverseCanvas />);

    expect(mockCanvas).toHaveBeenLastCalledWith("always");
  });

  it("stops rendering when hidden and resumes when visible", () => {
    render(<UniverseCanvas />);

    act(() => {
      hidden = true;
      document.dispatchEvent(new Event("visibilitychange"));
    });

    expect(mockCanvas).toHaveBeenLastCalledWith("never");

    act(() => {
      hidden = false;
      document.dispatchEvent(new Event("visibilitychange"));
    });

    expect(mockCanvas).toHaveBeenLastCalledWith("always");
  });
});

