package com.riskaggregator.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import com.riskaggregator.model.Priority;
import com.riskaggregator.model.RiskFinding;
import com.riskaggregator.model.RiskSummary;

import java.io.IOException;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.EnumMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

public final class RiskSummaryService {

    private final ObjectMapper objectMapper;

    public RiskSummaryService() {
        this.objectMapper = new ObjectMapper().registerModule(new JavaTimeModule());
    }

    public RiskSummary loadFromFile(Path jsonPath) throws IOException {
        RiskSummary summary = objectMapper.readValue(jsonPath.toFile(), RiskSummary.class);
        validate(summary);
        return summary;
    }

    private void validate(RiskSummary summary) {
        if (summary.getFindings() == null) {
            throw new IllegalStateException("risk summary has no findings array");
        }
        for (RiskFinding finding : summary.getFindings()) {
            if (finding.getAccountId() == null || finding.getAccountId().isBlank()) {
                throw new IllegalStateException("finding missing account_id: " + finding.getFindingId());
            }
        }
    }

    public List<RiskFinding> sortedByRiskDescending(RiskSummary summary) {
        return summary.getFindings().stream()
                .sorted(Comparator.comparingInt(RiskFinding::getRiskScore).reversed())
                .collect(Collectors.toList());
    }

    public Map<Priority, List<RiskFinding>> groupByPriority(RiskSummary summary) {
        Map<Priority, List<RiskFinding>> grouped = new EnumMap<>(Priority.class);
        for (Priority priority : Priority.values()) {
            grouped.put(priority, new java.util.ArrayList<>());
        }
        for (RiskFinding finding : summary.getFindings()) {
            grouped.get(finding.getPriority()).add(finding);
        }
        return grouped;
    }

    public List<RiskFinding> topN(RiskSummary summary, int n) {
        return sortedByRiskDescending(summary).stream().limit(n).collect(Collectors.toList());
    }

    public double averageRiskScore(RiskSummary summary) {
        return summary.getFindings().stream()
                .mapToInt(RiskFinding::getRiskScore)
                .average()
                .orElse(0.0);
    }
}
