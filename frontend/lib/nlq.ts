import type { Priority, RiskFinding } from "@/lib/schemas/risk";

export interface ParsedQuery {
  priority?: Priority;
  categoryKeywords: string[];
  minScore?: number;
  maxScore?: number;
  freeText?: string;
}

const PRIORITY_KEYWORDS: Record<Priority, string[]> = {
  CRITICAL: ["critical"],
  HIGH: ["high"],
  MEDIUM: ["medium", "med"],
  LOW: ["low"],
};

const CATEGORY_SYNONYMS: Record<string, string[]> = {
  STRUCTURING: ["structuring", "structure", "ctr", "cash deposit"],
  HIGH_RISK_GEOGRAPHY: ["geography", "geo", "jurisdiction", "sanction", "country"],
  RAPID_FUND_MOVEMENT: ["rapid", "movement", "layering"],
  DORMANT_REACTIVATION: ["dormant", "reactivat"],
  PEP_CROSS_BORDER: ["pep", "politically exposed", "cross-border", "cross border"],
  DEVICE_CHANGE_LARGE_TRANSFER: ["takeover", "device change"],
  SHARED_DEVICE_FINGERPRINT: ["shared device", "fingerprint", "linked device"],
  SHARED_IP_ADDRESS: ["shared ip", "ip address", "same ip"],
  SHARED_BENEFICIARY: ["beneficiary", "mule", "linked account", "network"],
  EXTERNAL_ALERT: ["alert", "watchlist", "adverse media", "fraud alert"],
};

function extractScoreBound(question: string, pattern: RegExp): number | undefined {
  const match = question.match(pattern);
  return match ? Number(match[1]) : undefined;
}

export function parseQuery(question: string): ParsedQuery {
  const q = question.toLowerCase();

  const priority = (Object.keys(PRIORITY_KEYWORDS) as Priority[]).find((p) =>
    PRIORITY_KEYWORDS[p].some((kw) => q.includes(kw))
  );

  const categoryKeywords = Object.keys(CATEGORY_SYNONYMS).filter((category) =>
    CATEGORY_SYNONYMS[category].some((kw) => q.includes(kw))
  );

  const minScore = extractScoreBound(q, /(?:above|over|greater than|>)\s*(\d+)/);
  const maxScore = extractScoreBound(q, /(?:below|under|less than|<)\s*(\d+)/);

  const accountMatch = q.match(/acc-?\d+/i);
  const freeText = accountMatch ? accountMatch[0].toUpperCase().replace(/^ACC-?/, "ACC-") : undefined;

  return { priority, categoryKeywords, minScore, maxScore, freeText };
}

export function applyParsedQuery(findings: RiskFinding[], parsed: ParsedQuery): RiskFinding[] {
  return findings.filter((f) => {
    if (parsed.priority && f.priority !== parsed.priority) return false;
    if (parsed.minScore !== undefined && f.risk_score < parsed.minScore) return false;
    if (parsed.maxScore !== undefined && f.risk_score > parsed.maxScore) return false;
    if (parsed.freeText && !f.account_id.toUpperCase().includes(parsed.freeText)) return false;
    if (parsed.categoryKeywords.length > 0) {
      const matchesAnyCategory = parsed.categoryKeywords.some((cat) =>
        f.categories.includes(cat)
      );
      if (!matchesAnyCategory) return false;
    }
    return true;
  });
}

export function answerLocally(
  question: string,
  findings: RiskFinding[]
): { answer: string; matched_finding_ids: string[] } {
  const parsed = parseQuery(question);
  const hasAnySignal =
    parsed.priority !== undefined ||
    parsed.categoryKeywords.length > 0 ||
    parsed.minScore !== undefined ||
    parsed.maxScore !== undefined ||
    parsed.freeText !== undefined;

  if (!hasAnySignal) {
    return {
      answer: "I didn't recognize a filter in that question. Try a priority (critical/high/medium/low), a category (structuring, geography, PEP, shared device, shared beneficiary...), an account id, or a score threshold (e.g. \"above 70\").",
      matched_finding_ids: [],
    };
  }

  const matches = applyParsedQuery(findings, parsed);

  if (matches.length === 0) {
    return {
      answer: "No findings matched that query.",
      matched_finding_ids: [],
    };
  }

  const top = matches.slice(0, 5);
  const summary = top
    .map((f) => `${f.account_id} (${f.priority.toLowerCase()}, score ${f.risk_score})`)
    .join(", ");
  const more = matches.length > top.length ? ` and ${matches.length - top.length} more` : "";

  return {
    answer: `Found ${matches.length} matching finding(s): ${summary}${more}.`,
    matched_finding_ids: matches.map((f) => f.finding_id),
  };
}
