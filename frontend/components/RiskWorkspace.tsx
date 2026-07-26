"use client";

import { useState } from "react";
import type { RiskFinding } from "@/types/risk";
import NlqChat from "./NlqChat";
import FindingsExplorer from "./FindingsExplorer";

export default function RiskWorkspace({ findings }: { findings: RiskFinding[] }) {
  const [nlqFilterIds, setNlqFilterIds] = useState<string[] | null>(null);

  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
      <div className="lg:col-span-1">
        <NlqChat onResult={setNlqFilterIds} />
      </div>
      <div className="lg:col-span-2">
        <FindingsExplorer findings={findings} restrictToIds={nlqFilterIds} />
      </div>
    </div>
  );
}
