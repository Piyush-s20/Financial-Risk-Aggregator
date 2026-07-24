package com.riskaggregator.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;
import java.util.Objects;

@JsonIgnoreProperties(ignoreUnknown = true)
public final class RiskFinding {

    @JsonProperty("finding_id")
    private String findingId;

    @JsonProperty("account_id")
    private String accountId;

    @JsonProperty("customer_name")
    private String customerName;

    @JsonProperty("risk_score")
    private int riskScore;

    @JsonProperty("priority")
    private Priority priority;

    @JsonProperty("categories")
    private List<String> categories;

    @JsonProperty("rationale")
    private String rationale;

    @JsonProperty("evidence_refs")
    private List<String> evidenceRefs;

    @JsonProperty("confidence")
    private Confidence confidence;

    @JsonProperty("recommended_action")
    private String recommendedAction;

    public RiskFinding() {
    }

    public String getFindingId() {
        return findingId;
    }

    public void setFindingId(String findingId) {
        this.findingId = findingId;
    }

    public String getAccountId() {
        return accountId;
    }

    public void setAccountId(String accountId) {
        this.accountId = accountId;
    }

    public String getCustomerName() {
        return customerName;
    }

    public void setCustomerName(String customerName) {
        this.customerName = customerName;
    }

    public int getRiskScore() {
        return riskScore;
    }

    public void setRiskScore(int riskScore) {
        if (riskScore < 0 || riskScore > 100) {
            throw new IllegalArgumentException("riskScore must be within [0, 100]: " + riskScore);
        }
        this.riskScore = riskScore;
    }

    public Priority getPriority() {
        return priority;
    }

    public void setPriority(Priority priority) {
        this.priority = priority;
    }

    public List<String> getCategories() {
        return categories;
    }

    public void setCategories(List<String> categories) {
        this.categories = categories;
    }

    public String getRationale() {
        return rationale;
    }

    public void setRationale(String rationale) {
        this.rationale = rationale;
    }

    public List<String> getEvidenceRefs() {
        return evidenceRefs;
    }

    public void setEvidenceRefs(List<String> evidenceRefs) {
        this.evidenceRefs = evidenceRefs;
    }

    public Confidence getConfidence() {
        return confidence;
    }

    public void setConfidence(Confidence confidence) {
        this.confidence = confidence;
    }

    public String getRecommendedAction() {
        return recommendedAction;
    }

    public void setRecommendedAction(String recommendedAction) {
        this.recommendedAction = recommendedAction;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof RiskFinding that)) return false;
        return Objects.equals(findingId, that.findingId);
    }

    @Override
    public int hashCode() {
        return Objects.hash(findingId);
    }

    @Override
    public String toString() {
        return "RiskFinding{" + findingId + ", " + accountId + ", score=" + riskScore
                + ", priority=" + priority + "}";
    }
}
