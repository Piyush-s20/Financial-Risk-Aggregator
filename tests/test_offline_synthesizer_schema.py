import pytest
from pydantic import ValidationError

from offline_synthesizer import synthesize
from schemas import RiskSummary


@pytest.fixture
def fused_dataset():
    return {
        "accounts": [
            {
                "account_id": "ACC-1",
                "customer_name": "Alice Example",
                "pep_flag": False,
                "kyc_risk_rating": "LOW",
            },
            {
                "account_id": "ACC-2",
                "customer_name": "Bob Example",
                "pep_flag": True,
                "kyc_risk_rating": "HIGH",
            },
            {
                "account_id": "ACC-3",
                "customer_name": "Carol Example",
                "pep_flag": False,
                "kyc_risk_rating": "LOW",
            },
        ],
        "external_alerts": [
            "STRUCTURING PATTERN: Automated monitoring detected suspicious deposits to ACC-1.",
            "GENERAL NOTE: Routine quarterly KYC refresh completed for ACC-3. No material changes identified.",
        ],
    }


@pytest.fixture
def detector_signals():
    return [
        {
            "account_id": "ACC-1",
            "signal_type": "STRUCTURING",
            "severity": "HIGH",
            "description": "3 transactions just under the $10,000 reporting threshold within 7 days.",
            "evidence": ["T1", "T2", "T3"],
        },
        {
            "account_id": "ACC-2",
            "signal_type": "PEP_CROSS_BORDER",
            "severity": "MEDIUM",
            "description": "PEP-flagged account with cross-border transactions.",
            "evidence": ["T4"],
        },
    ]


def test_synthesize_output_validates_against_pydantic_schema(fused_dataset, detector_signals):
    result = synthesize(fused_dataset, detector_signals)
    result["generation_mode"] = "offline_fallback"

    validated = RiskSummary.model_validate(result)

    assert validated.accounts_reviewed == 3
    assert len(validated.findings) >= 1
    assert all(0 <= f.risk_score <= 100 for f in validated.findings)


def test_synthesize_findings_are_sorted_by_risk_score_descending(fused_dataset, detector_signals):
    result = synthesize(fused_dataset, detector_signals)
    scores = [f["risk_score"] for f in result["findings"]]

    assert scores == sorted(scores, reverse=True)


def test_synthesize_excludes_purely_informational_alerts(fused_dataset, detector_signals):
    result = synthesize(fused_dataset, detector_signals)

    flagged_accounts = {f["account_id"] for f in result["findings"]}

    assert "ACC-3" not in flagged_accounts


def test_synthesize_output_rejects_when_findings_not_sorted():
    bad_summary = {
        "generated_at": "2026-01-01T00:00:00+00:00",
        "accounts_reviewed": 2,
        "generation_mode": "offline_fallback",
        "portfolio_summary": "test",
        "findings": [
            {
                "finding_id": "FIND-001",
                "account_id": "ACC-1",
                "customer_name": "Alice",
                "risk_score": 10,
                "priority": "LOW",
                "categories": ["EXTERNAL_ALERT"],
                "rationale": "test",
                "evidence_refs": [],
                "confidence": "LOW",
                "recommended_action": "test",
            },
            {
                "finding_id": "FIND-002",
                "account_id": "ACC-2",
                "customer_name": "Bob",
                "risk_score": 90,
                "priority": "CRITICAL",
                "categories": ["STRUCTURING"],
                "rationale": "test",
                "evidence_refs": [],
                "confidence": "HIGH",
                "recommended_action": "test",
            },
        ],
    }

    with pytest.raises(ValidationError):
        RiskSummary.model_validate(bad_summary)
