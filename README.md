# Financial Risk Signal Aggregator

AI prototype that ingests structured transaction data, account activity, and unstructured
external alerts, correlates them per account, and produces a prioritised, analyst-ready
risk summary.

## Approach

Four stages, each owned by the stack best suited to it:

1. **Ingest** (`data_pipeline/generate_mock_data.py`, Python/Pandas) — produces a synthetic
   dataset: `transactions.csv`, `account_activity.json`, `external_alerts.txt`.
2. **Detect** (`backend/anomaly_detector.py`, Python/Pandas) — deterministic rules scan the
   fused transaction/account data for structuring, high-risk-geography exposure, rapid fund
   movement, dormant-account reactivation, PEP cross-border activity, and device-change +
   large-transfer patterns. This gives the LLM stage a grounded, auditable starting point
   instead of asking it to spot anomalies in raw rows.
3. **Synthesize** (`backend/gemini_client.py`, `backend/prompt_templates.py`) — the detector
   signals, fused account data, and external alert text are sent to the **Gemini API** with a
   fixed JSON schema (see `backend/prompt_templates.py:RESPONSE_SCHEMA`). Gemini correlates
   signals across sources, assigns a 0-100 risk score and priority, and writes a rationale
   grounded in the evidence it was given. If `GEMINI_API_KEY` is not set, `backend/offline_synthesizer.py`
   reproduces the same JSON contract with rule-based scoring, so the pipeline and dashboard
   run end-to-end with no API key (`generation_mode` in the output records which path ran).
4. **Review** — `datamodels/` (Java) models the same JSON contract as typed POJOs, validates
   it, and exposes grouping/sorting used by an internal case-management style backend.
   `frontend/` (Next.js + Tailwind) renders the same file as a dashboard: KPI tiles, a
   priority breakdown, and a filterable/searchable findings table with an expandable
   rationale + evidence view.

All four stages read/write one shared contract: `output/risk_summary.json` (schema in
`backend/prompt_templates.py`), copied to `frontend/public/data/risk_summary.json` for the
dashboard.

## Tools used

- **Python 3 + Pandas** — mock data generation, ingestion, fusion, rule-based anomaly detection
- **Gemini API** (`google-generativeai`, `gemini-2.5-flash` by default) — risk correlation,
  scoring, and rationale generation, with a deterministic offline fallback for demoing without
  an API key
- **Java 17 + Jackson + Maven** — typed data models and an internal validation/prioritisation
  service over the risk summary JSON
- **Next.js 14 (App Router) + TypeScript + Tailwind CSS** — the compliance-facing dashboard

## Data assumptions

- All data is synthetic, generated with a fixed random seed (`SEED = 42`) for reproducibility —
  no proprietary or client data is used.
- 25 accounts, ~400-450 transactions over a 45-day window, with a handful of transactions and
  alerts deliberately injected to trigger each detector rule (structuring, high-risk geography,
  rapid movement, dormant reactivation) so the demo has something to find.
- External alerts are short freeform text blocks, as a stand-in for watchlist hits, adverse
  media, sanctions screening, and fraud system output — the kind of unstructured signal that
  doesn't fit a transaction schema.
- `$10,000` is used as the illustrative CTR/structuring threshold; thresholds throughout
  (`backend/anomaly_detector.py`) are placeholders to be tuned against real policy in a
  production setting, not calibrated against actual regulatory guidance.
- A purely informational alert ("routine KYC refresh, no material change") is deliberately
  included and is *not* surfaced as a finding — evidence the system doesn't just flag every
  alert it sees.

## Setup

**1. Generate mock data + run the risk engine (Python 3.10+)**
```bash
pip install -r requirements.txt
python data_pipeline/generate_mock_data.py
cd backend
export GEMINI_API_KEY=your_key_here   # optional — omit to use the offline fallback
python risk_engine.py
```
Writes `output/risk_summary.json` and copies it to `frontend/public/data/risk_summary.json`.

**2. Java data models (JDK 17+, Maven)**
```bash
cd datamodels && mvn -q compile exec:java
```
Loads `../output/risk_summary.json`, validates it, and prints findings grouped by priority.

**3. Dashboard (Node 18+)**
```bash
cd frontend && npm install && npm run dev
```
Open `http://localhost:3000`. Re-run step 1 and refresh to pick up new data (`npm run build`
for a production bundle — it inlines whatever is in `public/data/risk_summary.json` at build time).

## Example: input → output

**Input** — one transaction row (`data/transactions.csv`):
```
transaction_id,account_id,timestamp,amount,...,country,channel
TXN-STRU-8161,ACC-1003,2026-06-26T00:00:00,9800.00,...,US,WIRE
TXN-STRU-6580,ACC-1003,2026-06-27T03:00:00,9700.00,...,CA,WIRE
TXN-STRU-1485,ACC-1003,2026-06-28T06:00:00,9650.00,...,GB,WIRE
```
plus a matching external alert (`data/external_alerts.txt`):
```
STRUCTURING PATTERN: Automated monitoring detected three cash-equivalent deposits to
ACC-1003 within a 7-day window, each just under the $10,000 CTR reporting threshold.
```

**Output** — the corresponding entry in `output/risk_summary.json`:
```json
{
  "finding_id": "FIND-001",
  "account_id": "ACC-1003",
  "customer_name": "Customer 3",
  "risk_score": 50,
  "priority": "HIGH",
  "categories": ["EXTERNAL_ALERT", "STRUCTURING"],
  "rationale": "3 transactions just under the $10,000 reporting threshold within 7 days. STRUCTURING PATTERN.",
  "evidence_refs": ["TXN-STRU-8161", "TXN-STRU-6580", "TXN-STRU-1485", "ALERT: STRUCTURING PATTERN: ..."],
  "confidence": "HIGH",
  "recommended_action": "File internal SAR draft; request source-of-funds documentation."
}
```
The dashboard renders this as a "High" priority row; clicking it expands the rationale and
evidence identifiers shown above.

## Possible enhancements

Natural-language query interface over the risk summary; multi-turn analyst chat grounded in
the same evidence refs; a feedback loop where analyst dispositions retrain detector thresholds;
richer entity resolution across accounts sharing a beneficial owner.
