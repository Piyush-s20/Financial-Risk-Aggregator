import { NextRequest, NextResponse } from "next/server";
import { loadRiskSummary } from "@/lib/loadRiskSummary";
import { answerLocally } from "@/lib/nlq";
import { callGeminiJson, GeminiUnavailableError } from "@/lib/gemini";
import { NlqRequestSchema, GEMINI_NLQ_RESPONSE_SCHEMA, type NlqResponse } from "@/lib/schemas/nlq";

export const dynamic = "force-dynamic";

const SYSTEM_INSTRUCTION = `You are a compliance analyst assistant answering questions about a \
list of already-generated financial risk findings. Answer ONLY using the findings JSON you are \
given — never invent accounts, scores, or categories that aren't present. Keep the answer to 1-3 \
sentences. matched_finding_ids must contain the finding_id of every finding referenced in your \
answer, and nothing else. If nothing matches, return an empty array and say so.`;

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const parsed = NlqRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.message }, { status: 400 });
  }

  const summary = await loadRiskSummary();
  const { question } = parsed.data;

  try {
    const result = await callGeminiJson<{ answer: string; matched_finding_ids: string[] }>({
      systemInstruction: SYSTEM_INSTRUCTION,
      userContent: `Findings:\n${JSON.stringify(summary.findings)}\n\nQuestion: ${question}`,
      responseSchema: GEMINI_NLQ_RESPONSE_SCHEMA,
    });
    const response: NlqResponse = { ...result, mode: "gemini" };
    return NextResponse.json(response);
  } catch (err) {
    if (!(err instanceof GeminiUnavailableError)) {
      console.error("Gemini NLQ call failed, falling back to offline parser:", err);
    }
    const fallback = answerLocally(question, summary.findings);
    const response: NlqResponse = { ...fallback, mode: "offline_fallback" };
    return NextResponse.json(response);
  }
}
