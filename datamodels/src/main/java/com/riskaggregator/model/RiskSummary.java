package com.riskaggregator.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

import java.time.OffsetDateTime;
import java.util.List;

@JsonIgnoreProperties(ignoreUnknown = true)
public final class RiskSummary {

    @JsonProperty("generated_at")
    private OffsetDateTime generatedAt;

    @JsonProperty("accounts_reviewed")
    private int accountsReviewed;

    @JsonProperty("findings")
    private List<RiskFinding> findings;

    @JsonProperty("portfolio_summary")
    private String portfolioSummary;

    @JsonProperty("generation_mode")
    private GenerationMode generationMode;

    public RiskSummary() {
    }

    public OffsetDateTime getGeneratedAt() {
        return generatedAt;
    }

    public void setGeneratedAt(OffsetDateTime generatedAt) {
        this.generatedAt = generatedAt;
    }

    public int getAccountsReviewed() {
        return accountsReviewed;
    }

    public void setAccountsReviewed(int accountsReviewed) {
        this.accountsReviewed = accountsReviewed;
    }

    public List<RiskFinding> getFindings() {
        return findings;
    }

    public void setFindings(List<RiskFinding> findings) {
        this.findings = findings;
    }

    public String getPortfolioSummary() {
        return portfolioSummary;
    }

    public void setPortfolioSummary(String portfolioSummary) {
        this.portfolioSummary = portfolioSummary;
    }

    public GenerationMode getGenerationMode() {
        return generationMode;
    }

    public void setGenerationMode(GenerationMode generationMode) {
        this.generationMode = generationMode;
    }
}
