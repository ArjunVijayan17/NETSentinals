"""Rebuild standard_scaler.joblib from the raw CICIDS2017 MachineLearningCSV.

Exact reproduction of the cleaning + split + StandardScaler fit from
``notebooks/01_load_and_clean_data.ipynb``, so the scaler stats match what the
committed models expect. Feature selection is skipped (the 20 features are
already known); StandardScaler is per-column, so fitting on just those 20
columns yields identical mean_/scale_ values.

Usage:
    python backend/scripts/rebuild_scaler.py <csv_dir> <out_scaler.joblib>
"""
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

warnings.filterwarnings("ignore")

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.app.config import REQUIRED_FEATURES  # noqa: E402

DAMAGED_SEPARATORS = (chr(0xFFFD), chr(0x96), chr(0x2013), chr(0x2014))
ATTACK_CATEGORIES = {
    "Web Attack - Brute Force": "Web Attack",
    "Web Attack - Sql Injection": "Web Attack",
    "Web Attack - XSS": "Web Attack",
}
LABEL_COLUMNS = ["attack_label", "attack_category", "is_attack"]


def clean_label_names(labels):
    cleaned = labels.astype("string").str.strip()
    for char in DAMAGED_SEPARATORS:
        cleaned = cleaned.str.replace(char, "-", regex=False)
    return cleaned.str.replace(r"\s+", " ", regex=True)


def to_category(labels):
    return labels.map(lambda name: ATTACK_CATEGORIES.get(name, name)).astype("string")


def load_clean(csv_dir: Path) -> pd.DataFrame:
    files = sorted(csv_dir.glob("*.csv"))
    print(f"CSV files: {len(files)}")

    frames = []
    for f in files:
        df = pd.read_csv(f, low_memory=False)
        df.columns = df.columns.str.strip()
        feature_cols = [c for c in df.columns if c != "Label"]
        for c in feature_cols:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        df.replace([np.inf, -np.inf], np.nan, inplace=True)
        df[feature_cols] = df[feature_cols].astype("float32")
        frames.append(df)

    data = pd.concat(frames, ignore_index=True)
    del frames

    data["Label"] = clean_label_names(data["Label"])
    data.dropna(inplace=True)

    repeated_column = "Fwd Header Length.1"
    if repeated_column in data.columns:
        if not data[repeated_column].equals(data["Fwd Header Length"]):
            raise ValueError(f"{repeated_column} is not an exact copy")
        data.drop(columns=repeated_column, inplace=True)

    data.drop_duplicates(inplace=True)
    data.rename(columns={"Label": "attack_label"}, inplace=True)
    data["attack_category"] = to_category(data["attack_label"])
    data["is_attack"] = (data["attack_label"] != "BENIGN").astype("int8")

    return data.reset_index(drop=True)


def stratification_labels(data):
    strata = data["attack_label"].astype(str)
    counts = strata.map(strata.value_counts())
    strata = strata.where(counts >= 2, other="RARE")
    if strata.value_counts().min() < 2:
        return data["is_attack"]
    return strata


def main():
    csv_dir = Path(sys.argv[1])
    out_path = Path(sys.argv[2])

    data = load_clean(csv_dir)
    print(f"Cleaned rows: {len(data):,}  (expect 2,497,980)")

    missing = [f for f in REQUIRED_FEATURES if f not in data.columns]
    if missing:
        raise ValueError(f"Missing required features after cleaning: {missing}")

    feature_columns = [c for c in data.columns if c not in LABEL_COLUMNS]
    x = data[feature_columns]
    labels = data[LABEL_COLUMNS]

    x_train, x_test, _, _ = train_test_split(
        x,
        labels,
        test_size=0.20,
        random_state=42,
        stratify=stratification_labels(data),
    )
    print(f"Train rows: {len(x_train):,}  Test rows: {len(x_test):,}")

    scaler = StandardScaler()
    scaler.fit(x_train[REQUIRED_FEATURES].astype("float64"))
    joblib.dump(scaler, out_path)
    print(f"Saved scaler: {out_path}")
    print(f"Features: {len(REQUIRED_FEATURES)}")
    print("mean_ sample:", np.round(scaler.mean_[:5], 3))
    print("scale_ sample:", np.round(scaler.scale_[:5], 3))


if __name__ == "__main__":
    main()
