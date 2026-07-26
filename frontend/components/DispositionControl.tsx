"use client";

import { DISPOSITION_LABELS, type DispositionStatus } from "@/lib/schemas/disposition";

const OPTIONS: { status: DispositionStatus; label: string; activeClass: string }[] = [
  { status: "TRUE_POSITIVE", label: "TP", activeClass: "bg-risk-critical text-white" },
  { status: "FALSE_POSITIVE", label: "FP", activeClass: "bg-risk-good text-white" },
  { status: "ESCALATED", label: "Esc", activeClass: "bg-risk-warning text-zinc-900" },
];

export default function DispositionControl({
  current,
  onChange,
  disabled,
}: {
  current?: DispositionStatus;
  onChange: (status: DispositionStatus) => void;
  disabled?: boolean;
}) {
  return (
    <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
      {OPTIONS.map((opt) => (
        <button
          key={opt.status}
          type="button"
          disabled={disabled}
          onClick={() => onChange(opt.status)}
          title={DISPOSITION_LABELS[opt.status]}
          aria-pressed={current === opt.status}
          className={`rounded px-1.5 py-0.5 text-[10px] font-semibold transition-colors disabled:opacity-40 ${
            current === opt.status
              ? opt.activeClass
              : "bg-zinc-100 text-zinc-500 hover:bg-zinc-200 dark:bg-zinc-800 dark:text-zinc-400 dark:hover:bg-zinc-700"
          }`}
        >
          {opt.label}
        </button>
      ))}
    </div>
  );
}
