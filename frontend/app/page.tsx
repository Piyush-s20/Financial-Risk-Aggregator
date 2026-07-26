import { loadRiskSummary } from "@/lib/loadRiskSummary";
import StatTile from "@/components/StatTile";
import PriorityDistribution from "@/components/PriorityDistribution";
import RiskWorkspace from "@/components/RiskWorkspace";

export const dynamic = "force-dynamic";

export default async function Home() {
  const summary = await loadRiskSummary();
  const critical = summary.findings.filter((f) => f.priority === "CRITICAL").length;
  const avgScore =
    summary.findings.reduce((acc, f) => acc + f.risk_score, 0) /
    Math.max(1, summary.findings.length);

  return (
    <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6 lg:px-8">
      <header className="flex flex-col gap-1 border-b border-zinc-200 pb-6 dark:border-zinc-800">
        <p className="text-xs font-semibold uppercase tracking-wide text-accent dark:text-accent-dark">
          Compliance &amp; Risk
        </p>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">
          Financial Risk Signal Aggregator
        </h1>
        <p className="max-w-3xl text-sm text-zinc-500 dark:text-zinc-400">
          {summary.portfolio_summary}
        </p>
        <p className="text-xs text-zinc-400 dark:text-zinc-500">
          Generated {new Date(summary.generated_at).toLocaleString()} &middot; source:{" "}
          {summary.generation_mode === "gemini" ? "Gemini API" : "offline rule-based fallback"}
        </p>
      </header>

      <section className="mt-6 grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatTile label="Accounts reviewed" value={String(summary.accounts_reviewed)} />
        <StatTile
          label="Flagged for review"
          value={String(summary.findings.length)}
          sublabel={`${Math.round(
            (summary.findings.length / Math.max(1, summary.accounts_reviewed)) * 100
          )}% of portfolio`}
        />
        <StatTile
          label="Critical priority"
          value={String(critical)}
          accentClassName="text-risk-critical"
        />
        <StatTile label="Average risk score" value={avgScore.toFixed(1)} />
      </section>

      <section className="mt-6 grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1">
          <PriorityDistribution findings={summary.findings} />
        </div>
        <div className="lg:col-span-2">
          <div className="h-full rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
            <h2 className="text-sm font-semibold text-zinc-700 dark:text-zinc-200">
              How this summary was produced
            </h2>
            <ol className="mt-3 space-y-2 text-sm text-zinc-600 dark:text-zinc-300">
              <li>
                <span className="font-semibold text-zinc-800 dark:text-zinc-100">1. Ingest.</span>{" "}
                Transaction CSV, account activity JSON, and unstructured external alert text are
                loaded and fused per account.
              </li>
              <li>
                <span className="font-semibold text-zinc-800 dark:text-zinc-100">2. Detect.</span>{" "}
                Deterministic rules flag structuring, high-risk geography, rapid fund movement,
                dormant reactivation, PEP cross-border activity, device-change takeover, and
                entity links (shared device fingerprints, IPs, or wire beneficiaries).
              </li>
              <li>
                <span className="font-semibold text-zinc-800 dark:text-zinc-100">3. Synthesize.</span>{" "}
                The Gemini API correlates detector signals with external alerts, scores risk
                0-100, and writes a grounded rationale per account.
              </li>
              <li>
                <span className="font-semibold text-zinc-800 dark:text-zinc-100">4. Review.</span>{" "}
                Analysts triage by priority, ask the chat panel plain-English questions, and
                record a True Positive / False Positive / Escalated disposition per finding.
              </li>
            </ol>
          </div>
        </div>
      </section>

      <section className="mt-6">
        <RiskWorkspace findings={summary.findings} />
      </section>
    </main>
  );
}
