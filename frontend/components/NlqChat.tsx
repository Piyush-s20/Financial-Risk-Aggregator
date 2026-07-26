"use client";

import { FormEvent, useState } from "react";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

export default function NlqChat({
  onResult,
}: {
  onResult: (ids: string[] | null) => void;
}) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [mode, setMode] = useState<"gemini" | "offline_fallback" | null>(null);
  const [active, setActive] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await fetch("/api/nlq", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "request failed");
      setMessages((prev) => [...prev, { role: "assistant", text: data.answer }]);
      setMode(data.mode);
      setActive(true);
      onResult(data.matched_finding_ids);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", text: "Something went wrong reaching the query service." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function clearFilter() {
    setActive(false);
    setMode(null);
    onResult(null);
  }

  return (
    <div className="flex h-full flex-col rounded-xl border border-zinc-200 bg-white dark:border-zinc-800 dark:bg-zinc-900">
      <div className="flex items-center justify-between border-b border-zinc-200 p-4 dark:border-zinc-800">
        <h2 className="text-sm font-semibold text-zinc-700 dark:text-zinc-200">
          Ask about the findings
        </h2>
        {active ? (
          <button
            onClick={clearFilter}
            className="text-xs font-medium text-accent hover:underline dark:text-accent-dark"
          >
            Clear filter
          </button>
        ) : null}
      </div>

      <div className="max-h-56 flex-1 space-y-3 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <p className="text-sm text-zinc-400 dark:text-zinc-500">
            Try &quot;critical findings&quot;, &quot;anything above 70&quot;, &quot;shared
            beneficiary&quot;, or &quot;ACC-1007&quot;.
          </p>
        ) : null}
        {messages.map((m, i) => (
          <div key={i} className={m.role === "user" ? "text-right" : "text-left"}>
            <span
              className={`inline-block max-w-[85%] rounded-lg px-3 py-2 text-sm ${
                m.role === "user"
                  ? "bg-accent text-white dark:bg-accent-dark"
                  : "bg-zinc-100 text-zinc-700 dark:bg-zinc-800 dark:text-zinc-200"
              }`}
            >
              {m.text}
            </span>
          </div>
        ))}
        {loading ? <p className="text-xs text-zinc-400 dark:text-zinc-500">Thinking…</p> : null}
      </div>

      <form
        onSubmit={submit}
        className="flex items-center gap-2 border-t border-zinc-200 p-3 dark:border-zinc-800"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question about the risk findings..."
          className="flex-1 rounded-lg border border-zinc-300 bg-white px-3 py-1.5 text-sm text-zinc-900 placeholder:text-zinc-400 focus:border-accent focus:outline-none focus:ring-1 focus:ring-accent dark:border-zinc-700 dark:bg-zinc-950 dark:text-zinc-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="rounded-lg bg-zinc-900 px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40 dark:bg-zinc-50 dark:text-zinc-900"
        >
          Ask
        </button>
      </form>
      {mode ? (
        <p className="px-4 pb-3 text-[11px] text-zinc-400 dark:text-zinc-500">
          Answered via {mode === "gemini" ? "Gemini API" : "offline rule-based parser"}
        </p>
      ) : null}
    </div>
  );
}
