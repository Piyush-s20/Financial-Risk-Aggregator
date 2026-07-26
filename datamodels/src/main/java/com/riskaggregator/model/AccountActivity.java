package com.riskaggregator.model;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonIgnoreProperties(ignoreUnknown = true)
public final class AccountActivity {

    @JsonProperty("account_id")
    private String accountId;

    @JsonProperty("customer_name")
    private String customerName;

    @JsonProperty("account_open_date")
    private String accountOpenDate;

    @JsonProperty("country_of_residence")
    private String countryOfResidence;

    @JsonProperty("kyc_risk_rating")
    private String kycRiskRating;

    @JsonProperty("avg_monthly_volume_usd")
    private double avgMonthlyVolumeUsd;

    @JsonProperty("pep_flag")
    private boolean pepFlag;

    @JsonProperty("login_count_30d")
    private int loginCount30d;

    @JsonProperty("days_since_last_activity")
    private int daysSinceLastActivity;

    @JsonProperty("device_change_flag_30d")
    private boolean deviceChangeFlag30d;

    @JsonProperty("device_fingerprint")
    private String deviceFingerprint;

    @JsonProperty("last_login_ip")
    private String lastLoginIp;

    public AccountActivity() {
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

    public String getAccountOpenDate() {
        return accountOpenDate;
    }

    public void setAccountOpenDate(String accountOpenDate) {
        this.accountOpenDate = accountOpenDate;
    }

    public String getCountryOfResidence() {
        return countryOfResidence;
    }

    public void setCountryOfResidence(String countryOfResidence) {
        this.countryOfResidence = countryOfResidence;
    }

    public String getKycRiskRating() {
        return kycRiskRating;
    }

    public void setKycRiskRating(String kycRiskRating) {
        this.kycRiskRating = kycRiskRating;
    }

    public double getAvgMonthlyVolumeUsd() {
        return avgMonthlyVolumeUsd;
    }

    public void setAvgMonthlyVolumeUsd(double avgMonthlyVolumeUsd) {
        this.avgMonthlyVolumeUsd = avgMonthlyVolumeUsd;
    }

    public boolean isPepFlag() {
        return pepFlag;
    }

    public void setPepFlag(boolean pepFlag) {
        this.pepFlag = pepFlag;
    }

    public int getLoginCount30d() {
        return loginCount30d;
    }

    public void setLoginCount30d(int loginCount30d) {
        this.loginCount30d = loginCount30d;
    }

    public int getDaysSinceLastActivity() {
        return daysSinceLastActivity;
    }

    public void setDaysSinceLastActivity(int daysSinceLastActivity) {
        this.daysSinceLastActivity = daysSinceLastActivity;
    }

    public boolean isDeviceChangeFlag30d() {
        return deviceChangeFlag30d;
    }

    public void setDeviceChangeFlag30d(boolean deviceChangeFlag30d) {
        this.deviceChangeFlag30d = deviceChangeFlag30d;
    }

    public String getDeviceFingerprint() {
        return deviceFingerprint;
    }

    public void setDeviceFingerprint(String deviceFingerprint) {
        this.deviceFingerprint = deviceFingerprint;
    }

    public String getLastLoginIp() {
        return lastLoginIp;
    }

    public void setLastLoginIp(String lastLoginIp) {
        this.lastLoginIp = lastLoginIp;
    }
}
