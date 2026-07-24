package com.riskaggregator.model;

public enum Priority {
    CRITICAL(3),
    HIGH(2),
    MEDIUM(1),
    LOW(0);

    private final int rank;

    Priority(int rank) {
        this.rank = rank;
    }

    public int rank() {
        return rank;
    }
}
