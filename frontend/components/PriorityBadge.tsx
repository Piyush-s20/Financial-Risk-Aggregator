import type { Priority } from "@/types/risk";

const STYLES: Record<Priority, { dot: string; text: string; ring: string; label: string }> = {
  CRITICAL: {
    dot: "bg-risk-critical",
    text: "text-risk-critical",
    ring: "ring-risk-critical/30",
    label: "Critical",
  },
  HIGH: {
    dot: "bg-risk-serious",
    text: "text-risk-serious",
    ring: "ring-risk-serious/30",
    label: "High",
  },
  MEDIUM: {
    dot: "bg-risk-warning",
    text: "text-amber-700 dark:text-risk-warning",
    ring: "ring-risk-warning/30",
    label: "Medium",
  },
  LOW: {
    dot: "bg-risk-good",
    text: "text-risk-good",
    ring: "ring-risk-good/30",
    label: "Low",
  },
};

export default function PriorityBadge({ priority }: { priority: Priority }) {
  const style = STYLES[priority];
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ring-1 ${style.ring} bg-zinc-100 dark:bg-zinc-800`}
    >
      <span className={`h-2 w-2 rounded-full ${style.dot}`} aria-hidden="true" />
      <span className={style.text}>{style.label}</span>
    </span>
  );
}
