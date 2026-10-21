"""
verify_models.py — Phase 0 sanity check

Loads all 4 model artifacts, runs a single synthetic prediction row,
and prints the result. Run from the project root:

    python backend/scripts/verify_models.py
"""
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

# Suppress sklearn version mismatch warnings for this script
warnings.filterwarnings("ignore", category=UserWarning)

# Allow imports from backend/
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.config import MODEL_PATHS, REQUIRED_FEATURES, BINARY_LABELS, SCALER_PATH
import joblib


def load_model(name: str, path: Path):
    print(f"\n{'='*50}")
    print(f"Loading: {name}")
    print(f"Path:    {path}")
    if not path.exists():
        print(f"  ❌ FILE NOT FOUND: {path}")
        return None
    model = joblib.load(path)
    print(f"  ✅ Loaded — type: {type(model).__name__}")
    return model


def make_test_row() -> pd.DataFrame:
    """A single row of synthetic but plausible feature values."""
    values = {
        "Packet Length Variance":     1000.0,
        "Packet Length Std":          31.6,
        "Bwd Packet Length Std":      20.0,
        "Average Packet Size":        150.0,
        "Avg Bwd Segment Size":       120.0,
        "Destination Port":           80.0,
        "Fwd IAT Max":                500000.0,
        "Fwd IAT Std":                200000.0,
        "Subflow Bwd Bytes":          300.0,
        "Fwd Packet Length Max":      400.0,
        "Flow IAT Std":               300000.0,
        "Init_Win_bytes_backward":    65535.0,
        "Fwd IAT Total":              1000000.0,
        "Idle Min":                   0.0,
        "Avg Fwd Segment Size":       150.0,
        "Total Length of Fwd Packets": 600.0,
        "Init_Win_bytes_forward":     65535.0,
        "Fwd IAT Mean":               250000.0,
        "Flow IAT Mean":              200000.0,
        "Min Packet Length":          40.0,
    }
    return pd.DataFrame([values])[REQUIRED_FEATURES]


def run_verify():
    print("NetSentinel — Model Verification Script")
    print("=" * 50)

    test_row = make_test_row()
    print(f"\nTest row shape: {test_row.shape}")
    print(f"Features: {list(test_row.columns)}")

    # The models were trained on Z-scored features; apply the training scaler.
    if not SCALER_PATH.exists():
        print(f"  ❌ SCALER NOT FOUND: {SCALER_PATH}")
        print("  Predictions below use raw features and will be wrong.")
    else:
        scaler = joblib.load(SCALER_PATH)
        test_row = pd.DataFrame(
            scaler.transform(test_row), columns=REQUIRED_FEATURES
        )
        print(f"  ✅ Standardized test row with: {SCALER_PATH}")

    results = {}

    # --- Binary models ---
    for name in ("random_forest", "decision_tree", "knn"):
        model = load_model(name, MODEL_PATHS[name])
        if model is None:
            continue
        pred    = model.predict(test_row)[0]
        proba   = model.predict_proba(test_row)[0]
        label   = BINARY_LABELS[int(pred)]
        conf    = float(proba[int(pred)])
        print(f"  Prediction: {pred} → {label}  (confidence: {conf:.4f})")
        print(f"  Probabilities: Benign={proba[0]:.4f}, Attack={proba[1]:.4f}")
        results[name] = {"label": label, "confidence": conf}

    # --- Multiclass model ---
    atk_model = load_model("attack_type", MODEL_PATHS["attack_type"])
    if atk_model is not None:
        pred    = atk_model.predict(test_row)[0]
        proba   = atk_model.predict_proba(test_row)[0]
        conf    = float(np.max(proba))
        print(f"  Prediction: {pred}  (confidence: {conf:.4f})")
        results["attack_type"] = {"category": pred, "confidence": conf}

    print("\n" + "=" * 50)
    print("Summary:")
    for k, v in results.items():
        print(f"  {k:25s}: {v}")

    if len(results) == 4:
        print("\n✅ All 4 models loaded and predicted successfully.")
    else:
        print(f"\n⚠️  Only {len(results)}/4 models verified. Check errors above.")


if __name__ == "__main__":
    run_verify()
