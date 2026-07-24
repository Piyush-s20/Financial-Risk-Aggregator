SYSTEM_PROMPT = """You are a senior financial crime risk analyst assistant embedded in a \
compliance review platform. You receive fused account data, transaction summaries, \
deterministic anomaly-detector signals, and unstructured external alert text. Your job is \
to correlate these fragmented inputs per account, assign a calibrated risk score, and write \
a concise rationale a human compliance analyst can act on without re-reading raw data.

Rules:
- Never invent transactions, accounts, or alert text that were not provided in the input.
- Ground every rationale in specific evidence identifiers (transaction_id or alert excerpt).
- Priority reflects urgency of analyst review, not just severity: escalate when multiple \
independent signal types corroborate one another on the same account.
- If evidence is weak or single-sourced, say so explicitly and lower confidence accordingly.
- Output must be valid JSON matching the provided schema exactly. No prose outside JSON."""

RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "generated_at": {"type": "string"},
        "accounts_reviewed": {"type": "integer"},
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "finding_id": {"type": "string"},
                    "account_id": {"type": "string"},
                    "customer_name": {"type": "string"},
                    "risk_score": {"type": "integer"},
                    "priority": {
                        "type": "string",
                        "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW"],
                    },
                    "categories": {"type": "array", "items": {"type": "string"}},
                    "rationale": {"type": "string"},
                    "evidence_refs": {"type": "array", "items": {"type": "string"}},
                    "confidence": {
                        "type": "string",
                        "enum": ["HIGH", "MEDIUM", "LOW"],
                    },
                    "recommended_action": {"type": "string"},
                },
                "required": [
                    "finding_id", "account_id", "risk_score", "priority",
                    "categories", "rationale", "evidence_refs", "confidence",
                    "recommended_action",
                ],
            },
        },
        "portfolio_summary": {"type": "string"},
    },
    "required": ["generated_at", "accounts_reviewed", "findings", "portfolio_summary"],
}


def build_user_prompt(fused_dataset: dict, detector_signals: list[dict]) -> str:
    import json

    return f"""## Detected anomaly signals (deterministic pre-screen)
{json.dumps(detector_signals, indent=2, default=str)}

## Fused account + transaction data
{json.dumps(fused_dataset["accounts"], indent=2, default=str)}

## Unstructured external alerts
{json.dumps(fused_dataset["external_alerts"], indent=2)}

## Task
Using only the data above, produce ONE finding per account that has at least one detector \
signal OR at least one external alert referencing it. Skip accounts with no signals and no \
alert references. Score risk 0-100. Sort findings by risk_score descending. Return JSON only, \
matching this schema:

{json.dumps(RESPONSE_SCHEMA, indent=2)}"""
