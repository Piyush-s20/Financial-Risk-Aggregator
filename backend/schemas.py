from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, field_validator


class Priority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class GenerationMode(str, Enum):
    GEMINI = "gemini"
    OFFLINE_FALLBACK = "offline_fallback"


class RiskFinding(BaseModel):
    finding_id: str
    account_id: str
    customer_name: str
    risk_score: int = Field(ge=0, le=100)
    priority: Priority
    categories: list[str]
    rationale: str
    evidence_refs: list[str]
    confidence: Confidence
    recommended_action: str

    @field_validator("categories")
    @classmethod
    def categories_not_empty(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("categories must not be empty")
        return value


class RiskSummary(BaseModel):
    generated_at: datetime
    accounts_reviewed: int = Field(ge=0)
    findings: list[RiskFinding]
    portfolio_summary: str
    generation_mode: GenerationMode

    @field_validator("findings")
    @classmethod
    def findings_sorted_descending(cls, value: list[RiskFinding]) -> list[RiskFinding]:
        scores = [f.risk_score for f in value]
        if scores != sorted(scores, reverse=True):
            raise ValueError("findings must be sorted by risk_score descending")
        return value
