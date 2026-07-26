import hashlib
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

OUT_DIR = Path(__file__).resolve().parent.parent / "data"
OUT_DIR.mkdir(parents=True, exist_ok=True)

ACCOUNT_IDS = [f"ACC-{1000 + i}" for i in range(25)]
HIGH_RISK_COUNTRIES = ["IR", "KP", "SY", "MM"]
NORMAL_COUNTRIES = ["US", "GB", "DE", "SG", "CA", "AU"]
MERCHANTS = ["Amazon", "Shell Gas", "Wire Transfer", "Crypto Exchange Alpha",
             "Offshore Holdings LLC", "Grocery Mart", "ATM Withdrawal",
             "Consulting Fees Ltd", "Payroll Inc", "Cash Deposit Kiosk"]
CHANNELS = ["ACH", "WIRE", "CARD", "ATM", "P2P"]
CUSTOMER_NAMES = [f"Customer {i}" for i in range(len(ACCOUNT_IDS))]

NORMAL_COUNTERPARTIES = [
    ("BEN-1001", "Alex Rivera"),
    ("BEN-1002", "Morgan Lee"),
    ("BEN-1003", "Jordan Kim"),
    ("BEN-1004", "Taylor Brooks"),
    ("BEN-1005", "Casey Nguyen"),
]

# Entity-resolution scenarios: pairs of accounts linked by a shared device
# fingerprint, login IP, or wire beneficiary that no single-account rule would
# surface on its own.
LINKED_DEVICE_PAIR = ("ACC-1003", "ACC-1021")
LINKED_DEVICE_FINGERPRINT = "FP-9F31C7A0"
LINKED_IP_PAIR = ("ACC-1012", "ACC-1024")
LINKED_IP_ADDRESS = "10.44.201.77"
LINKED_BENEFICIARY_PAIR = ("ACC-1004", "ACC-1015")
LINKED_BENEFICIARY = ("BEN-0099", "Rapid Settlement Corp")


def generate_transactions(n=400):
    rows = []
    start = datetime(2026, 6, 1)
    for i in range(n):
        account_id = random.choice(ACCOUNT_IDS)
        ts = start + timedelta(
            days=random.randint(0, 45),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
        )
        amount = round(np.random.lognormal(mean=6.0, sigma=1.1), 2)
        country = random.choice(NORMAL_COUNTRIES)
        merchant = random.choice(MERCHANTS)
        channel = random.choice(CHANNELS)
        counterparty_id, counterparty_name = (
            random.choice(NORMAL_COUNTERPARTIES) if channel in ("WIRE", "P2P") else ("", "")
        )
        rows.append({
            "transaction_id": f"TXN-{i:05d}",
            "account_id": account_id,
            "timestamp": ts.isoformat(),
            "amount": amount,
            "currency": "USD",
            "merchant": merchant,
            "country": country,
            "channel": channel,
            "mcc_code": random.choice([5411, 6011, 4829, 7995, 6051, 5999]),
            "counterparty_id": counterparty_id,
            "counterparty_name": counterparty_name,
        })

    injected = [
        ("ACC-1003", "structuring_pattern", 9800.00),
        ("ACC-1003", "structuring_pattern", 9700.00),
        ("ACC-1003", "structuring_pattern", 9650.00),
        ("ACC-1007", "high_risk_geo", 42000.00),
        ("ACC-1012", "rapid_movement", 87000.00),
        ("ACC-1012", "rapid_movement", 86500.00),
        ("ACC-1019", "dormant_reactivation", 61000.00),
        (LINKED_BENEFICIARY_PAIR[0], "shared_beneficiary", 15500.00),
        (LINKED_BENEFICIARY_PAIR[1], "shared_beneficiary", 18200.00),
    ]
    tag_base_offset = {
        "structuring_pattern": timedelta(days=25),
        "high_risk_geo": timedelta(days=30),
        "rapid_movement": timedelta(days=33),
        "dormant_reactivation": timedelta(days=38),
        "shared_beneficiary": timedelta(days=27),
    }
    tag_occurrence = {}
    for account_id, tag, amount in injected:
        occurrence = tag_occurrence.get(tag, 0)
        tag_occurrence[tag] = occurrence + 1
        if tag == "structuring_pattern":
            jitter = timedelta(days=occurrence, hours=occurrence * 3)
        elif tag == "rapid_movement":
            jitter = timedelta(hours=occurrence * 20)
        elif tag == "shared_beneficiary":
            jitter = timedelta(days=occurrence * 2, hours=occurrence * 5)
        else:
            jitter = timedelta(hours=random.randint(0, 6))
        ts = start + tag_base_offset[tag] + jitter
        country = random.choice(HIGH_RISK_COUNTRIES) if tag == "high_risk_geo" else random.choice(NORMAL_COUNTRIES)
        merchant = "Crypto Exchange Alpha" if tag == "rapid_movement" else "Offshore Holdings LLC" if tag == "high_risk_geo" else "Cash Deposit Kiosk"
        counterparty_id, counterparty_name = (
            LINKED_BENEFICIARY if tag == "shared_beneficiary" else ("", "")
        )
        rows.append({
            "transaction_id": f"TXN-{tag[:4].upper()}-{random.randint(1000,9999)}",
            "account_id": account_id,
            "timestamp": ts.isoformat(),
            "amount": amount,
            "currency": "USD",
            "merchant": merchant,
            "country": country,
            "channel": "WIRE" if tag == "shared_beneficiary" else random.choice(["WIRE", "P2P"]),
            "mcc_code": 6051,
            "counterparty_id": counterparty_id,
            "counterparty_name": counterparty_name,
            "_synthetic_tag": tag,
        })

    df = pd.DataFrame(rows).sort_values("timestamp").reset_index(drop=True)
    return df


def generate_account_activity():
    accounts = []
    for idx, account_id in enumerate(ACCOUNT_IDS):
        pep_flag = account_id in ("ACC-1007", "ACC-1015")
        dormant = account_id == "ACC-1019"
        digest = int(hashlib.sha256(account_id.encode()).hexdigest(), 16)
        device_fingerprint = f"FP-{digest % 0xFFFFFF:06X}"
        last_login_ip = f"10.{(digest >> 16) % 256}.{(digest >> 8) % 256}.{digest % 256}"
        if account_id in LINKED_DEVICE_PAIR:
            device_fingerprint = LINKED_DEVICE_FINGERPRINT
        if account_id in LINKED_IP_PAIR:
            last_login_ip = LINKED_IP_ADDRESS
        accounts.append({
            "account_id": account_id,
            "customer_name": CUSTOMER_NAMES[idx],
            "account_open_date": (datetime(2019, 1, 1) + timedelta(days=idx * 61)).date().isoformat(),
            "country_of_residence": random.choice(NORMAL_COUNTRIES),
            "kyc_risk_rating": random.choice(["LOW", "LOW", "MEDIUM", "HIGH"]),
            "avg_monthly_volume_usd": round(np.random.lognormal(mean=8.5, sigma=0.6), 2),
            "pep_flag": pep_flag,
            "login_count_30d": 0 if dormant else random.randint(2, 40),
            "days_since_last_activity": random.randint(180, 400) if dormant else random.randint(0, 5),
            "device_change_flag_30d": random.random() < 0.15,
            "device_fingerprint": device_fingerprint,
            "last_login_ip": last_login_ip,
        })
    return accounts


EXTERNAL_ALERTS = [
    "WATCHLIST HIT: Entity 'Offshore Holdings LLC' partially matches OFAC SDN list entry (score 0.82). "
    "Associated account ACC-1007 flagged for enhanced due diligence review.",

    "ADVERSE MEDIA: News search returned a 2026-06-18 article referencing 'Consulting Fees Ltd' in connection "
    "with an ongoing regulatory inquiry in a EU jurisdiction. No confirmed link to account holder identity yet.",

    "SANCTIONS SCREEN: Cross-border wire from ACC-1007 routed through a jurisdiction on the FATF high-risk list "
    "(counterparty country: IR). Screening engine confidence: HIGH.",

    "FRAUD ALERT: Device fingerprint for ACC-1012 changed twice within 48 hours immediately preceding two "
    "large outbound transfers to a crypto exchange. Pattern consistent with account takeover.",

    "DORMANT ACCOUNT REACTIVATION: ACC-1019 had no login or transaction activity for 11 months, then received "
    "a large inbound deposit followed by an immediate outbound transfer within the same business day.",

    "PEP SCREENING: Account holder for ACC-1007 identified as a politically exposed person (domestic PEP, "
    "government-adjacent role). Existing enhanced monitoring plan on file since account opening.",

    "STRUCTURING PATTERN: Automated monitoring detected three cash-equivalent deposits to ACC-1003 within a "
    "7-day window, each just under the $10,000 CTR reporting threshold.",

    "GENERAL NOTE: Routine quarterly KYC refresh completed for ACC-1001, ACC-1002, and ACC-1004. No material "
    "changes to risk profile identified.",
]


def generate_external_alerts():
    return "\n\n".join(EXTERNAL_ALERTS) + "\n"


def main():
    tx_df = generate_transactions()
    tx_path = OUT_DIR / "transactions.csv"
    tx_df.drop(columns=["_synthetic_tag"]).to_csv(tx_path, index=False)

    accounts = generate_account_activity()
    acc_path = OUT_DIR / "account_activity.json"
    acc_path.write_text(json.dumps(accounts, indent=2))

    alerts_path = OUT_DIR / "external_alerts.txt"
    alerts_path.write_text(generate_external_alerts())

    print(f"Wrote {len(tx_df)} transactions -> {tx_path}")
    print(f"Wrote {len(accounts)} account records -> {acc_path}")
    print(f"Wrote external alerts -> {alerts_path}")


if __name__ == "__main__":
    main()
