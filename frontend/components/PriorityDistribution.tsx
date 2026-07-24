import { PRIORITY_ORDER, type RiskFinding } from "@/types/risk";

const BAR_COLOR: Record<string, string> = {
  CRITICAL: "bg-risk-critical",
  HIGH: "bg-risk-serious",
  MEDIUM: "bg-risk-warning",
  LOW: "bg-risk-good",
};

export default function PriorityDistribution({ findings }: { findings: RiskFinding[] }) {
  const counts = PRIORITY_ORDER.map((priority) => ({
    priority,
    count: findings.filter((f) => f.priority === priority).length,
  }));
  const max = Math.max(1, ...counts.map((c) => c.count));

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <h2 className="text-sm font-semibold text-zinc-700 dark:text-zinc-200">
        Flagged accounts by priority
      </h2>
      <div className="mt-4 space-y-3">
        {counts.map(({ priority, count }) => (
          <div key={priority} className="flex items-center gap-3">
            <span className="w-16 shrink-0 text-xs font-medium text-zinc-500 dark:text-zinc-400">
              {priority}
            </span>
            <div className="h-4 flex-1 rounded-full bg-zinc-100 dark:bg-zinc-800">
              <div
                className={`h-4 rounded-full ${BAR_COLOR[priority]}`}
                style={{ width: `${(count / max) * 100}%` }}
              />
            </div>
            <span className="w-6 shrink-0 text-right text-xs font-semibold tabular text-zinc-700 dark:text-zinc-200">
              {count}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
