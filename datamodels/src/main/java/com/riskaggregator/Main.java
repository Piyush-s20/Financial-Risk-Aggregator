package com.riskaggregator;

import com.riskaggregator.model.Priority;
import com.riskaggregator.model.RiskFinding;
import com.riskaggregator.model.RiskSummary;
import com.riskaggregator.service.RiskSummaryService;

import java.nio.file.Path;
import java.util.List;
import java.util.Map;

public final class Main {

    public static void main(String[] args) throws Exception {
        Path jsonPath = args.length > 0
                ? Path.of(args[0])
                : Path.of("..", "output", "risk_summary.json");

        RiskSummaryService service = new RiskSummaryService();
        RiskSummary summary = service.loadFromFile(jsonPath);

        System.out.printf("Accounts reviewed: %d%n", summary.getAccountsReviewed());
        System.out.printf("Generation mode: %s%n", summary.getGenerationMode());
        System.out.printf("Average risk score: %.1f%n", service.averageRiskScore(summary));
        System.out.println(summary.getPortfolioSummary());
        System.out.println();

        Map<Priority, List<RiskFinding>> byPriority = service.groupByPriority(summary);
        for (Priority priority : Priority.values()) {
            List<RiskFinding> findings = byPriority.get(priority);
            if (findings.isEmpty()) {
                continue;
            }
            System.out.printf("== %s (%d) ==%n", priority, findings.size());
            for (RiskFinding finding : findings) {
                System.out.printf("  [%d] %s (%s) - %s%n",
                        finding.getRiskScore(), finding.getAccountId(),
                        finding.getCustomerName(), finding.getRecommendedAction());
            }
        }
    }
}
