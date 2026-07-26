import { promises as fs } from "fs";
import path from "path";
import { parseRiskSummary, type RiskSummary } from "@/lib/schemas/risk";

const RISK_SUMMARY_PATH = path.join(process.cwd(), "public", "data", "risk_summary.json");

export async function loadRiskSummary(): Promise<RiskSummary> {
  const raw = await fs.readFile(RISK_SUMMARY_PATH, "utf-8");
  return parseRiskSummary(JSON.parse(raw));
}
