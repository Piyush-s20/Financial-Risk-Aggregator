from datetime import timedelta

import pandas as pd

CTR_THRESHOLD = 10000
STRUCTURING_WINDOW_DAYS = 7
STRUCTURING_MIN_COUNT = 3
STRUCTURING_FLOOR_RATIO = 0.85
RAPID_MOVEMENT_WINDOW_HOURS = 72
RAPID_MOVEMENT_MIN_USD = 50000
HIGH_RISK_COUNTRIES = {"IR", "KP", "SY", "MM"}
DORMANT_INACTIVITY_DAYS = 180
# A beneficiary shared by more than a handful of accounts is a common payment
# recipient (payroll processor, utility, marketplace), not a mule cluster —
# cap cluster size so high-volume everyday counterparties aren't flagged.
MAX_SHARED_BENEFICIARY_ACCOUNTS = 4


def detect_structuring(tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    for account_id, group in tx_df.groupby("account_id"):
        near_threshold = group[
            (group["amount"] >= CTR_THRESHOLD * STRUCTURING_FLOOR_RATIO)
            & (group["amount"] < CTR_THRESHOLD)
        ].sort_values("timestamp")
        if len(near_threshold) < STRUCTURING_MIN_COUNT:
            continue
        timestamps = near_threshold["timestamp"].tolist()
        for i in range(len(timestamps) - STRUCTURING_MIN_COUNT + 1):
            window = timestamps[i : i + STRUCTURING_MIN_COUNT]
            if window[-1] - window[0] <= timedelta(days=STRUCTURING_WINDOW_DAYS):
                signals.append({
                    "account_id": account_id,
                    "signal_type": "STRUCTURING",
                    "severity": "HIGH",
                    "description": (
                        f"{len(near_threshold)} transactions just under the "
                        f"${CTR_THRESHOLD:,} reporting threshold within "
                        f"{STRUCTURING_WINDOW_DAYS} days."
                    ),
                    "evidence": near_threshold["transaction_id"].tolist(),
                })
                break
    return signals


def detect_high_risk_geography(tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    flagged = tx_df[tx_df["country"].isin(HIGH_RISK_COUNTRIES)]
    for account_id, group in flagged.groupby("account_id"):
        signals.append({
            "account_id": account_id,
            "signal_type": "HIGH_RISK_GEOGRAPHY",
            "severity": "HIGH",
            "description": (
                f"{len(group)} transaction(s) routed through high-risk "
                f"jurisdictions: {sorted(group['country'].unique().tolist())}."
            ),
            "evidence": group["transaction_id"].tolist(),
        })
    return signals


def detect_rapid_movement(tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    for account_id, group in tx_df.groupby("account_id"):
        group = group.sort_values("timestamp")
        for i in range(len(group)):
            window_start = group.iloc[i]["timestamp"]
            window_end = window_start + timedelta(hours=RAPID_MOVEMENT_WINDOW_HOURS)
            window = group[
                (group["timestamp"] >= window_start) & (group["timestamp"] <= window_end)
            ]
            if window["amount"].sum() >= RAPID_MOVEMENT_MIN_USD and len(window) >= 2:
                signals.append({
                    "account_id": account_id,
                    "signal_type": "RAPID_FUND_MOVEMENT",
                    "severity": "MEDIUM",
                    "description": (
                        f"${window['amount'].sum():,.2f} moved across "
                        f"{len(window)} transactions within "
                        f"{RAPID_MOVEMENT_WINDOW_HOURS}h."
                    ),
                    "evidence": window["transaction_id"].tolist(),
                })
                break
    return signals


def detect_dormant_reactivation(accounts: list[dict], tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    for account in accounts:
        if account["days_since_last_activity"] < DORMANT_INACTIVITY_DAYS:
            continue
        account_tx = tx_df[tx_df["account_id"] == account["account_id"]]
        if account_tx.empty:
            continue
        signals.append({
            "account_id": account["account_id"],
            "signal_type": "DORMANT_REACTIVATION",
            "severity": "MEDIUM",
            "description": (
                f"Account inactive for {account['days_since_last_activity']} days "
                f"before {len(account_tx)} new transaction(s) appeared."
            ),
            "evidence": account_tx["transaction_id"].tolist(),
        })
    return signals


def detect_pep_cross_border(accounts: list[dict], tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    for account in accounts:
        if not account.get("pep_flag"):
            continue
        cross_border = tx_df[
            (tx_df["account_id"] == account["account_id"])
            & (tx_df["country"] != account["country_of_residence"])
        ]
        if cross_border.empty:
            continue
        signals.append({
            "account_id": account["account_id"],
            "signal_type": "PEP_CROSS_BORDER",
            "severity": "MEDIUM",
            "description": (
                f"PEP-flagged account with {len(cross_border)} cross-border "
                f"transaction(s) outside country of residence "
                f"({account['country_of_residence']})."
            ),
            "evidence": cross_border["transaction_id"].tolist(),
        })
    return signals


def detect_device_change_large_transfer(accounts: list[dict], tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    for account in accounts:
        if not account.get("device_change_flag_30d"):
            continue
        large_tx = tx_df[
            (tx_df["account_id"] == account["account_id"])
            & (tx_df["amount"] >= RAPID_MOVEMENT_MIN_USD / 2)
        ]
        if large_tx.empty:
            continue
        signals.append({
            "account_id": account["account_id"],
            "signal_type": "DEVICE_CHANGE_LARGE_TRANSFER",
            "severity": "HIGH",
            "description": (
                "Device fingerprint changed within 30 days, coinciding with "
                f"{len(large_tx)} large outbound transfer(s). Possible account takeover."
            ),
            "evidence": large_tx["transaction_id"].tolist(),
        })
    return signals


def detect_shared_device_fingerprint(accounts: list[dict]) -> list[dict]:
    signals = []
    groups: dict[str, list[str]] = {}
    for account in accounts:
        fingerprint = account.get("device_fingerprint")
        if not fingerprint:
            continue
        groups.setdefault(fingerprint, []).append(account["account_id"])

    for fingerprint, account_ids in groups.items():
        if len(account_ids) < 2:
            continue
        for account_id in account_ids:
            others = [a for a in account_ids if a != account_id]
            signals.append({
                "account_id": account_id,
                "signal_type": "SHARED_DEVICE_FINGERPRINT",
                "severity": "HIGH",
                "description": (
                    f"Device fingerprint {fingerprint} also used by "
                    f"{', '.join(others)} — possible mule network or shared access."
                ),
                "evidence": [f"DEVICE:{fingerprint}"] + others,
            })
    return signals


def detect_shared_ip_address(accounts: list[dict]) -> list[dict]:
    signals = []
    groups: dict[str, list[str]] = {}
    for account in accounts:
        ip = account.get("last_login_ip")
        if not ip:
            continue
        groups.setdefault(ip, []).append(account["account_id"])

    for ip, account_ids in groups.items():
        if len(account_ids) < 2:
            continue
        for account_id in account_ids:
            others = [a for a in account_ids if a != account_id]
            signals.append({
                "account_id": account_id,
                "signal_type": "SHARED_IP_ADDRESS",
                "severity": "MEDIUM",
                "description": (
                    f"Login IP {ip} also used by {', '.join(others)} within the "
                    "review window — corroborate with device data before escalating."
                ),
                "evidence": [f"IP:{ip}"] + others,
            })
    return signals


def detect_shared_beneficiary(tx_df: pd.DataFrame) -> list[dict]:
    signals = []
    with_counterparty = tx_df[
        tx_df["counterparty_id"].notna() & (tx_df["counterparty_id"] != "")
    ]
    for counterparty_id, group in with_counterparty.groupby("counterparty_id"):
        account_ids = sorted(group["account_id"].unique().tolist())
        if not (2 <= len(account_ids) <= MAX_SHARED_BENEFICIARY_ACCOUNTS):
            continue
        counterparty_name = group["counterparty_name"].iloc[0]
        for account_id in account_ids:
            others = [a for a in account_ids if a != account_id]
            own_tx = group[group["account_id"] == account_id]["transaction_id"].tolist()
            signals.append({
                "account_id": account_id,
                "signal_type": "SHARED_BENEFICIARY",
                "severity": "HIGH",
                "description": (
                    f"Also wires beneficiary '{counterparty_name}' ({counterparty_id}), "
                    f"shared with {', '.join(others)} — possible layering or mule network."
                ),
                "evidence": own_tx,
            })
    return signals


def run_all_detectors(tx_df: pd.DataFrame, accounts: list[dict]) -> list[dict]:
    signals = []
    signals += detect_structuring(tx_df)
    signals += detect_high_risk_geography(tx_df)
    signals += detect_rapid_movement(tx_df)
    signals += detect_dormant_reactivation(accounts, tx_df)
    signals += detect_pep_cross_border(accounts, tx_df)
    signals += detect_device_change_large_transfer(accounts, tx_df)
    signals += detect_shared_device_fingerprint(accounts)
    signals += detect_shared_ip_address(accounts)
    signals += detect_shared_beneficiary(tx_df)
    return signals
