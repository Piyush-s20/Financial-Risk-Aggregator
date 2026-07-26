import { z } from "zod";

export const DispositionStatusSchema = z.enum([
  "TRUE_POSITIVE",
  "FALSE_POSITIVE",
  "ESCALATED",
]);

export const DispositionRecordSchema = z.object({
  finding_id: z.string().min(1),
  status: DispositionStatusSchema,
  note: z.string().max(2000).optional(),
  updated_at: z.string(),
  updated_by: z.string().default("analyst"),
});

export const DispositionMapSchema = z.record(z.string(), DispositionRecordSchema);

export const DispositionUpdateRequestSchema = z.object({
  finding_id: z.string().min(1),
  status: DispositionStatusSchema,
  note: z.string().max(2000).optional(),
  updated_by: z.string().max(200).optional(),
});

export type DispositionStatus = z.infer<typeof DispositionStatusSchema>;
export type DispositionRecord = z.infer<typeof DispositionRecordSchema>;
export type DispositionMap = z.infer<typeof DispositionMapSchema>;
export type DispositionUpdateRequest = z.infer<typeof DispositionUpdateRequestSchema>;

export const DISPOSITION_LABELS: Record<DispositionStatus, string> = {
  TRUE_POSITIVE: "True Positive",
  FALSE_POSITIVE: "False Positive",
  ESCALATED: "Escalated",
};
