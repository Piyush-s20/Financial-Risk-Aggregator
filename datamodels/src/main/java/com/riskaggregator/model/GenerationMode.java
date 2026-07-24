package com.riskaggregator.model;

import com.fasterxml.jackson.annotation.JsonProperty;

public enum GenerationMode {
    @JsonProperty("gemini")
    GEMINI,
    @JsonProperty("offline_fallback")
    OFFLINE_FALLBACK
}
