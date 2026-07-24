import re
from collections import defaultdict
from datetime import datetime, timezone

SEVERITY_WEIGHT = {"HIGH": 35, "MEDIUM": 20, "LOW": 10}

CATEGORY_ACTION = {
    "STRUCTURING": "File internal SAR draft; request source-of-funds documentation.",
    "HIGH_RISK_GEOGRAPHY": "Escalate to sanctions/OFAC screening team for manual match review.",
    "RAPID_FUND_MOVEMENT": "Freeze pending transfers and contact customer to verify intent.",
    "DORMANT_REACTIVATION": "Verify identity via out-of-band contact before releasing funds.",
    "PEP_CROSS_BORDER": "Confirm enhanced due diligence plan is current; review with MLRO.",
    "DEVICE_CHANGE_LARGE_TRANSFER": "Suspend outbound transfers; trigger account takeover playbook.",
    "EXTERNAL_ALERT": "Cross-reference with case management system for prior alerts.",
}


NOISE_ALERT_PREFIXES = ("GENERAL NOTE:",)


def _match_alerts_to_accounts(alerts: list[str], account_ids: list[str]) -> dict:
    matches = defaultdict(list)
    for alert in alerts:
        if alert.startswith(NOISE_ALERT_PREFIXES):
            continue
        for account_id in account_ids:
            if account_id in alert:
                matches[account_id].append(alert)
    return matches


def synthesize(fused_dataset: dict, detector_signals: list[dict]) -> dict:
    accounts = {a["account_id"]: a for a in fused_dataset["accounts"]}
    alerts = fused_dataset["external_alerts"]
    account_ids = list(accounts.keys())
    alert_matches = _match_alerts_to_accounts(alerts, account_ids)

    signals_by_account = defaultdict(list)
    for signal in detector_signals:
        signals_by_account[signal["account_id"]].append(signal)

    involved_accounts = set(signals_by_account.keys()) | set(alert_matches.keys())

    findings = []
    for idx, account_id in enumerate(sorted(involved_accounts)):
        account = accounts.get(account_id, {})
        acct_signals = signals_by_account.get(account_id, [])
        acct_alerts = alert_matches.get(account_id, [])

        score = sum(SEVERITY_WEIGHT.get(s["severity"], 10) for s in acct_signals)
        score += 15 * len(acct_alerts)
        if account.get("pep_flag"):
            score += 10
        if account.get("kyc_risk_rating") == "HIGH":
            score += 10
        score = min(score, 99)

        distinct_types = {s["signal_type"] for s in acct_signals}
        if acct_alerts:
            distinct_types.add("EXTERNAL_ALERT")

        if score >= 75 or len(distinct_types) >= 3:
            priority = "CRITICAL"
        elif score >= 50:
            priority = "HIGH"
        elif score >= 25:
            priority = "MEDIUM"
        else:
            priority = "LOW"

        confidence = "HIGH" if (acct_signals and acct_alerts) else (
            "MEDIUM" if (acct_signals or acct_alerts) else "LOW"
        )

        rationale_parts = []
        for s in acct_signals:
            rationale_parts.append(s["description"])
        for a in acct_alerts:
            snippet = re.split(r"[:.]", a, maxsplit=1)
            rationale_parts.append(snippet[0].strip() + ".")
        rationale = " ".join(rationale_parts) or "No corroborating detail available."

        evidence_refs = []
        for s in acct_signals:
            evidence_refs.extend(s.get("evidence", []))
        evidence_refs.extend([f"ALERT: {a[:60]}..." for a in acct_alerts])

        action = CATEGORY_ACTION.get(
            next(iter(distinct_types), "EXTERNAL_ALERT"),
            "Route to analyst for manual review.",
        )

        findings.append({
            "finding_id": f"FIND-{idx+1:03d}",
            "account_id": account_id,
            "customer_name": account.get("customer_name", "Unknown"),
            "risk_score": score,
            "priority": priority,
            "categories": sorted(distinct_types),
            "rationale": rationale,
            "evidence_refs": evidence_refs,
            "confidence": confidence,
            "recommended_action": action,
        })

    findings.sort(key=lambda f: f["risk_score"], reverse=True)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "accounts_reviewed": len(accounts),
        "findings": findings,
        "portfolio_summary": (
            f"{len(findings)} of {len(accounts)} accounts flagged for review. "
            f"{sum(1 for f in findings if f['priority'] == 'CRITICAL')} critical, "
            f"{sum(1 for f in findings if f['priority'] == 'HIGH')} high priority. "
            "Top drivers: structuring, high-risk geography exposure, and rapid fund "
            "movement corroborated by external watchlist/adverse-media alerts."
        ),
    }
