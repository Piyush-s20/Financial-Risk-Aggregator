from datetime import datetime, timedelta

import pandas as pd
import pytest

from anomaly_detector import (
    MAX_SHARED_BENEFICIARY_ACCOUNTS,
    detect_shared_beneficiary,
    detect_shared_device_fingerprint,
    detect_shared_ip_address,
    detect_structuring,
)


def make_tx(transaction_id, account_id, timestamp, amount, **extra):
    row = {
        "transaction_id": transaction_id,
        "account_id": account_id,
        "timestamp": pd.Timestamp(timestamp),
        "amount": amount,
        "currency": "USD",
        "merchant": "Test Merchant",
        "country": "US",
        "channel": "WIRE",
        "mcc_code": 6051,
        "counterparty_id": "",
        "counterparty_name": "",
    }
    row.update(extra)
    return row


def test_detect_structuring_flags_three_near_threshold_transactions_within_window():
    base = datetime(2026, 1, 1)
    rows = [
        make_tx("T1", "ACC-1", base, 9800.00),
        make_tx("T2", "ACC-1", base + timedelta(days=2), 9700.00),
        make_tx("T3", "ACC-1", base + timedelta(days=4), 9650.00),
        make_tx("T4", "ACC-2", base, 250.00),
    ]
    tx_df = pd.DataFrame(rows)

    signals = detect_structuring(tx_df)

    assert len(signals) == 1
    assert signals[0]["account_id"] == "ACC-1"
    assert signals[0]["signal_type"] == "STRUCTURING"
    assert set(signals[0]["evidence"]) == {"T1", "T2", "T3"}


def test_detect_structuring_ignores_transactions_spread_beyond_window():
    base = datetime(2026, 1, 1)
    rows = [
        make_tx("T1", "ACC-1", base, 9800.00),
        make_tx("T2", "ACC-1", base + timedelta(days=10), 9700.00),
        make_tx("T3", "ACC-1", base + timedelta(days=20), 9650.00),
    ]
    tx_df = pd.DataFrame(rows)

    assert detect_structuring(tx_df) == []


def test_detect_structuring_ignores_amounts_below_the_floor_ratio():
    base = datetime(2026, 1, 1)
    rows = [
        make_tx("T1", "ACC-1", base, 500.00),
        make_tx("T2", "ACC-1", base + timedelta(days=1), 600.00),
        make_tx("T3", "ACC-1", base + timedelta(days=2), 700.00),
    ]
    tx_df = pd.DataFrame(rows)

    assert detect_structuring(tx_df) == []


def test_detect_shared_device_fingerprint_flags_linked_pair():
    accounts = [
        {"account_id": "ACC-1", "device_fingerprint": "FP-AAA"},
        {"account_id": "ACC-2", "device_fingerprint": "FP-AAA"},
        {"account_id": "ACC-3", "device_fingerprint": "FP-BBB"},
    ]

    signals = detect_shared_device_fingerprint(accounts)

    flagged_accounts = {s["account_id"] for s in signals}
    assert flagged_accounts == {"ACC-1", "ACC-2"}
    assert all(s["signal_type"] == "SHARED_DEVICE_FINGERPRINT" for s in signals)


def test_detect_shared_device_fingerprint_ignores_unique_fingerprints():
    accounts = [
        {"account_id": "ACC-1", "device_fingerprint": "FP-AAA"},
        {"account_id": "ACC-2", "device_fingerprint": "FP-BBB"},
    ]

    assert detect_shared_device_fingerprint(accounts) == []


def test_detect_shared_ip_address_flags_linked_pair():
    accounts = [
        {"account_id": "ACC-1", "last_login_ip": "10.0.0.1"},
        {"account_id": "ACC-2", "last_login_ip": "10.0.0.1"},
        {"account_id": "ACC-3", "last_login_ip": "10.0.0.2"},
    ]

    signals = detect_shared_ip_address(accounts)

    flagged_accounts = {s["account_id"] for s in signals}
    assert flagged_accounts == {"ACC-1", "ACC-2"}
    assert all(s["signal_type"] == "SHARED_IP_ADDRESS" for s in signals)


def test_detect_shared_beneficiary_flags_small_cluster():
    base = datetime(2026, 1, 1)
    rows = [
        make_tx("T1", "ACC-1", base, 15000, counterparty_id="BEN-1", counterparty_name="Suspicious LLC"),
        make_tx("T2", "ACC-2", base, 18000, counterparty_id="BEN-1", counterparty_name="Suspicious LLC"),
    ]
    tx_df = pd.DataFrame(rows)

    signals = detect_shared_beneficiary(tx_df)

    flagged_accounts = {s["account_id"] for s in signals}
    assert flagged_accounts == {"ACC-1", "ACC-2"}
    assert all(s["signal_type"] == "SHARED_BENEFICIARY" for s in signals)


def test_detect_shared_beneficiary_ignores_high_volume_common_counterparty():
    base = datetime(2026, 1, 1)
    account_count = MAX_SHARED_BENEFICIARY_ACCOUNTS + 5
    rows = [
        make_tx(f"T{i}", f"ACC-{i}", base, 100 + i, counterparty_id="BEN-COMMON", counterparty_name="Utility Co")
        for i in range(account_count)
    ]
    tx_df = pd.DataFrame(rows)

    assert detect_shared_beneficiary(tx_df) == []


def test_detect_shared_beneficiary_ignores_single_sender():
    base = datetime(2026, 1, 1)
    rows = [make_tx("T1", "ACC-1", base, 15000, counterparty_id="BEN-1", counterparty_name="Solo LLC")]
    tx_df = pd.DataFrame(rows)

    assert detect_shared_beneficiary(tx_df) == []
