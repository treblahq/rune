import { describe, expect, it } from "vitest";

import { findReviewMoments } from "./transcript";
import type { Transcript } from "@/lib/types/rune";

const transcript: Transcript = {
  job_id: "one",
  text: "Olá Rune.",
  language: "pt",
  duration: 2,
  segments: [
    {
      id: 0,
      start: 0,
      end: 2,
      text: "Olá Rune.",
      speaker: null,
      words: [
        { text: "Olá", start: 0, end: 0.5, confidence: 0.98 },
        { text: " Rune.", start: 0.5, end: 2, confidence: 0.48 },
      ],
    },
  ],
};

describe("findReviewMoments", () => {
  it("returns only words below the confidence threshold", () => {
    expect(findReviewMoments(transcript)).toEqual([
      { text: "Rune.", start: 0.5, confidence: 0.48, segmentId: 0 },
    ]);
  });
});
