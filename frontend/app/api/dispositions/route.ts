import { promises as fs } from "fs";
import path from "path";
import { NextRequest, NextResponse } from "next/server";
import {
  DispositionMapSchema,
  DispositionUpdateRequestSchema,
  type DispositionMap,
} from "@/lib/schemas/disposition";

export const dynamic = "force-dynamic";

const DISPOSITIONS_PATH = path.join(process.cwd(), "..", "output", "dispositions.json");

async function readDispositions(): Promise<DispositionMap> {
  try {
    const raw = await fs.readFile(DISPOSITIONS_PATH, "utf-8");
    return DispositionMapSchema.parse(JSON.parse(raw));
  } catch (err: any) {
    if (err?.code === "ENOENT") return {};
    throw err;
  }
}

async function writeDispositions(map: DispositionMap): Promise<void> {
  await fs.mkdir(path.dirname(DISPOSITIONS_PATH), { recursive: true });
  await fs.writeFile(DISPOSITIONS_PATH, JSON.stringify(map, null, 2));
}

export async function GET() {
  const dispositions = await readDispositions();
  return NextResponse.json(dispositions);
}

export async function POST(request: NextRequest) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ error: "invalid JSON body" }, { status: 400 });
  }

  const parsed = DispositionUpdateRequestSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.message }, { status: 400 });
  }

  const dispositions = await readDispositions();
  const record = {
    finding_id: parsed.data.finding_id,
    status: parsed.data.status,
    note: parsed.data.note,
    updated_at: new Date().toISOString(),
    updated_by: parsed.data.updated_by ?? "analyst",
  };
  dispositions[parsed.data.finding_id] = record;
  await writeDispositions(dispositions);

  return NextResponse.json(record);
}
