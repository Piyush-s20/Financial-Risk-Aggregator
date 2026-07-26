import { z } from "zod";

export const PrioritySchema = z.enum(["CRITICAL", "HIGH", "MEDIUM", "LOW"]);
export const ConfidenceSchema = z.enum(["HIGH", "MEDIUM", "LOW"]);
export const GenerationModeSchema = z.enum(["gemini", "offline_fallback"]);

export const RiskFindingSchema = z.object({
  finding_id: z.string().min(1),
  account_id: z.string().min(1),
  customer_name: z.string().min(1),
  risk_score: z.number().int().min(0).max(100),
  priority: PrioritySchema,
  categories: z.array(z.string()).min(1),
  rationale: z.string(),
  evidence_refs: z.array(z.string()),
  confidence: ConfidenceSchema,
  recommended_action: z.string(),
});

export const RiskSummarySchema = z.object({
  generated_at: z.string(),
  accounts_reviewed: z.number().int().min(0),
  findings: z.array(RiskFindingSchema),
  portfolio_summary: z.string(),
  generation_mode: GenerationModeSchema,
});

export type Priority = z.infer<typeof PrioritySchema>;
export type Confidence = z.infer<typeof ConfidenceSchema>;
export type GenerationMode = z.infer<typeof GenerationModeSchema>;
export type RiskFinding = z.infer<typeof RiskFindingSchema>;
export type RiskSummary = z.infer<typeof RiskSummarySchema>;

export const PRIORITY_ORDER: Priority[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];

export function parseRiskSummary(data: unknown): RiskSummary {
  const result = RiskSummarySchema.safeParse(data);
  if (!result.success) {
    throw new Error(
      `risk_summary.json failed schema validation: ${result.error.message}`
    );
  }
  return result.data;
}
