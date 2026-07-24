import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_transactions() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "transactions.csv", parse_dates=["timestamp"])
    return df


def load_account_activity() -> list[dict]:
    return json.loads((DATA_DIR / "account_activity.json").read_text())


def load_external_alerts() -> list[str]:
    raw = (DATA_DIR / "external_alerts.txt").read_text()
    return [block.strip() for block in raw.split("\n\n") if block.strip()]


def summarize_account_transactions(tx_df: pd.DataFrame) -> dict:
    grouped = tx_df.groupby("account_id").agg(
        transaction_count=("transaction_id", "count"),
        total_volume_usd=("amount", "sum"),
        max_transaction_usd=("amount", "max"),
        distinct_countries=("country", lambda s: sorted(set(s))),
        distinct_merchants=("merchant", lambda s: sorted(set(s))),
    )
    return grouped.to_dict(orient="index")


def build_fused_dataset() -> dict:
    tx_df = load_transactions()
    accounts = load_account_activity()
    alerts = load_external_alerts()
    tx_summary = summarize_account_transactions(tx_df)

    fused_accounts = []
    for account in accounts:
        account_id = account["account_id"]
        recent_tx = tx_df[tx_df["account_id"] == account_id].sort_values(
            "timestamp", ascending=False
        ).head(10)
        fused_accounts.append({
            **account,
            "transaction_summary": tx_summary.get(account_id, {}),
            "recent_transactions": json.loads(
                recent_tx.to_json(orient="records", date_format="iso")
            ),
        })

    return {
        "accounts": fused_accounts,
        "external_alerts": alerts,
    }


if __name__ == "__main__":
    fused = build_fused_dataset()
    print(json.dumps(fused, indent=2)[:2000])
