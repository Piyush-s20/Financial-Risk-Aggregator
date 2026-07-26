import { z } from "zod";

export const NlqRequestSchema = z.object({
  question: z.string().min(1).max(500),
});

export const NlqResponseSchema = z.object({
  answer: z.string(),
  matched_finding_ids: z.array(z.string()),
  mode: z.enum(["gemini", "offline_fallback"]),
});

export type NlqRequest = z.infer<typeof NlqRequestSchema>;
export type NlqResponse = z.infer<typeof NlqResponseSchema>;

// Schema handed to Gemini's generationConfig.responseSchema so the model's
// JSON reply can be parsed with the same guarantees as the offline fallback.
export const GEMINI_NLQ_RESPONSE_SCHEMA = {
  type: "object",
  properties: {
    answer: { type: "string" },
    matched_finding_ids: { type: "array", items: { type: "string" } },
  },
  required: ["answer", "matched_finding_ids"],
};
