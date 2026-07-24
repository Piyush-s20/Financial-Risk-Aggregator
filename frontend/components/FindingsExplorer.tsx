"use client";

import { Fragment, useMemo, useState } from "react";
import { PRIORITY_ORDER, type Priority, type RiskFinding } from "@/types/risk";
import PriorityBadge from "./PriorityBadge";

const FILTERS: Array<Priority | "ALL"> = ["ALL", ...PRIORITY_ORDER];

export default function FindingsExplorer({ findings }: { findings: RiskFinding[] }) {
  const [filter, setFilter] = useState<Priority | "ALL">("ALL");
  const [query, setQuery] = useState("");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return findings
      .filter((f) => filter === "ALL" || f.priority === filter)
      .filter(
        (f) =>
          q === "" ||
          f.account_id.toLowerCase().includes(q) ||
          f.customer_name.toLowerCase().includes(q) ||
          f.categories.some((c) => c.toLowerCase().includes(q))
      )
      .sort((a, b) => b.risk_score - a.risk_score);
  }, [findings, filter, query]);

  return (
    <div className="rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex flex-col gap-3 border-b border-zinc-200 p-4 dark:border-zinc-800 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex flex-wrap gap-2">
          {FILTERS.map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                filter === f
                  ? "bg-zinc-900 text-white dark:bg-zinc-50 dark:text-zinc-900"
                  : "bg-zinc-100 text-zinc-600 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-300 dark:hover:bg-zinc-700"
              }`}
            >
              {f === "ALL" ? "All" : f.charAt(0) + f.slice(1).toLowerCase()}
            </button>
          ))}
        </div>
        <input
          type="text"
          placeholder="Search account, customer, or category..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm text-zinc-900 placeholder:text-zinc-400 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50 sm:w-72"
        />
      </div>

      <div className="overflow-x-auto">
        <table className="w-full min-w-[860px] text-left text-sm">
          <thead>
            <tr className="border-b border-zinc-200 text-xs uppercase tracking-wide text-zinc-500 dark:border-zinc-800 dark:text-zinc-400">
              <th className="px-4 py-3 font-medium">Priority</th>
              <th className="px-4 py-3 font-medium">Score</th>
              <th className="px-4 py-3 font-medium">Account</th>
              <th className="px-4 py-3 font-medium">Categories</th>
              <th className="px-4 py-3 font-medium">Confidence</th>
              <th className="px-4 py-3 font-medium">Recommended action</th>
            </tr>
          </thead>
          <tbody>
            {visible.map((finding) => {
              const expanded = expandedId === finding.finding_id;
              return (
                <Fragment key={finding.finding_id}>
                  <tr
                    onClick={() =>
                      setExpandedId(expanded ? null : finding.finding_id)
                    }
                    className="cursor-pointer border-b border-zinc-100 last:border-0 hover:bg-zinc-50 dark:border-zinc-800/60 dark:hover:bg-zinc-800/40"
                  >
                    <td className="px-4 py-3">
                      <PriorityBadge priority={finding.priority} />
                    </td>
                    <td className="tabular px-4 py-3 font-semibold text-zinc-800 dark:text-zinc-100">
                      {finding.risk_score}
                    </td>
                    <td className="px-4 py-3">
                      <div className="font-medium text-zinc-800 dark:text-zinc-100">
                        {finding.account_id}
                      </div>
                      <div className="text-xs text-zinc-500 dark:text-zinc-400">
                        {finding.customer_name}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex flex-wrap gap-1">
                        {finding.categories.map((c) => (
                          <span
                            key={c}
                            className="rounded bg-zinc-100 px-1.5 py-0.5 text-[11px] font-medium text-zinc-600 dark:bg-zinc-800 dark:text-zinc-300"
                          >
                            {c.replaceAll("_", " ").toLowerCase()}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-300">
                      {finding.confidence.charAt(0) + finding.confidence.slice(1).toLowerCase()}
                    </td>
                    <td className="px-4 py-3 text-zinc-600 dark:text-zinc-300">
                      {finding.recommended_action}
                    </td>
                  </tr>
                  {expanded ? (
                    <tr className="border-b border-zinc-100 bg-zinc-50 dark:border-zinc-800/60 dark:bg-zinc-800/30">
                      <td colSpan={6} className="px-4 py-4">
                        <p className="text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                          AI rationale
                        </p>
                        <p className="mt-1 text-sm text-zinc-700 dark:text-zinc-200">
                          {finding.rationale}
                        </p>
                        <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-zinc-500 dark:text-zinc-400">
                          Evidence
                        </p>
                        <div className="mt-1 flex flex-wrap gap-1.5">
                          {finding.evidence_refs.map((ref, i) => (
                            <span
                              key={`${finding.finding_id}-ev-${i}`}
                              className="rounded border border-zinc-200 bg-white px-1.5 py-0.5 font-mono text-[11px] text-zinc-600 dark:border-zinc-700 dark:bg-zinc-900 dark:text-zinc-300"
                            >
                              {ref}
                            </span>
                          ))}
                        </div>
                      </td>
                    </tr>
                  ) : null}
                </Fragment>
              );
            })}
            {visible.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-zinc-500 dark:text-zinc-400">
                  No findings match the current filter.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  );
}
