import type { Transcript } from "@/lib/types/rune";

export type ReviewMoment = {
  text: string;
  start: number;
  confidence: number;
  segmentId: number;
};

export function findReviewMoments(
  transcript: Transcript,
  threshold = 0.65,
): ReviewMoment[] {
  return transcript.segments.flatMap((segment) =>
    segment.words
      .filter((word) => word.confidence !== null && word.confidence < threshold)
      .map((word) => ({
        text: word.text.trim(),
        start: word.start,
        confidence: word.confidence as number,
        segmentId: segment.id,
      })),
  );
}
