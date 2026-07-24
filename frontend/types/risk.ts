export type Priority = "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
export type Confidence = "HIGH" | "MEDIUM" | "LOW";
export type GenerationMode = "gemini" | "offline_fallback";

export interface RiskFinding {
  finding_id: string;
  account_id: string;
  customer_name: string;
  risk_score: number;
  priority: Priority;
  categories: string[];
  rationale: string;
  evidence_refs: string[];
  confidence: Confidence;
  recommended_action: string;
}

export interface RiskSummary {
  generated_at: string;
  accounts_reviewed: number;
  findings: RiskFinding[];
  portfolio_summary: string;
  generation_mode: GenerationMode;
}

export const PRIORITY_ORDER: Priority[] = ["CRITICAL", "HIGH", "MEDIUM", "LOW"];
