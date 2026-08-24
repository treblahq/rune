import { describe, expect, it } from "vitest";

import { formatDuration, splitMediaLinks } from "./format";

describe("formatDuration", () => {
  it("formats short and long media without noise", () => {
    expect(formatDuration(65)).toBe("1:05");
    expect(formatDuration(3_661)).toBe("1:01:01");
    expect(formatDuration(null)).toBe("Sem duração");
  });
});

describe("splitMediaLinks", () => {
  it("accepts lines and spaces, removes duplicates, and ignores blanks", () => {
    expect(
      splitMediaLinks(" https://example.com/a\nhttps://example.com/b https://example.com/a "),
    ).toEqual(["https://example.com/a", "https://example.com/b"]);
  });
});
