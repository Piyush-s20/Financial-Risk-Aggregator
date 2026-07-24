package com.riskaggregator.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public final class AnomalySignal {

    @JsonProperty("account_id")
    private String accountId;

    @JsonProperty("signal_type")
    private String signalType;

    @JsonProperty("severity")
    private Confidence severity;

    @JsonProperty("description")
    private String description;

    @JsonProperty("evidence")
    private List<String> evidence;

    public AnomalySignal() {
    }

    public String getAccountId() {
        return accountId;
    }

    public void setAccountId(String accountId) {
        this.accountId = accountId;
    }

    public String getSignalType() {
        return signalType;
    }

    public void setSignalType(String signalType) {
        this.signalType = signalType;
    }

    public Confidence getSeverity() {
        return severity;
    }

    public void setSeverity(Confidence severity) {
        this.severity = severity;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public List<String> getEvidence() {
        return evidence;
    }

    public void setEvidence(List<String> evidence) {
        this.evidence = evidence;
    }
}
