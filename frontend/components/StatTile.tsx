export default function StatTile({
  label,
  value,
  sublabel,
  accentClassName,
}: {
  label: string;
  value: string;
  sublabel?: string;
  accentClassName?: string;
}) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-4 dark:border-zinc-800 dark:bg-zinc-900">
      <p className="text-sm text-zinc-500 dark:text-zinc-400">{label}</p>
      <p className={`mt-1 text-3xl font-semibold ${accentClassName ?? "text-zinc-900 dark:text-zinc-50"}`}>
        {value}
      </p>
      {sublabel ? (
        <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">{sublabel}</p>
      ) : null}
    </div>
  );
}
