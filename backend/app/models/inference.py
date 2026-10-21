"""Inference service — binary + multiclass chained prediction.

Contract (see MODEL_CONTRACT.md):

- All four models consume the exact same 20 features in exact order.
- Binary models return class ``0`` (Benign) or ``1`` (Attack).
- The multiclass model runs only on rows classified as Attack.
- Confidence is ``predict_proba`` of the predicted class, reported as a
  model confidence score (not a guaranteed probability).
"""
from __future__ import annotations

from typing import Dict, List

import numpy as np
import pandas as pd

from ..config import BINARY_LABELS, REQUIRED_FEATURES
from .loader import get_models, get_scaler

BINARY_MODELS = ("random_forest", "decision_tree", "knn")


def _standardize(df: pd.DataFrame) -> pd.DataFrame:
    """Apply the training StandardScaler (raw features → Z-scored)."""
    scaler = get_scaler()
    X = scaler.transform(df)
    return pd.DataFrame(X, columns=df.columns, index=df.index)


def validate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and normalize a feature frame.

    Returns a copy with the 20 required columns selected in the exact
    training order. Raises ``ValueError`` on any schema violation.

    - strips whitespace from column names (CICIDS CSVs carry leading spaces)
    - checks all 20 features are present
    - checks all 20 features are numeric
    - checks no NaN or +/-Inf values are present
    """
    if df is None or df.empty:
        raise ValueError("Empty input: no rows to classify.")

    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]

    missing = [f for f in REQUIRED_FEATURES if f not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = df[REQUIRED_FEATURES]

    non_numeric = [
        c for c in REQUIRED_FEATURES if not pd.api.types.is_numeric_dtype(df[c])
    ]
    if non_numeric:
        raise ValueError(f"Non-numeric feature columns: {non_numeric}")

    df = df.replace([np.inf, -np.inf], np.nan)
    bad = df.isna().any(axis=1)
    if bad.any():
        raise ValueError(
            f"{int(bad.sum())} row(s) contain NaN or infinite values."
        )

    return df


def _binary_row_result(model, row: pd.DataFrame) -> Dict[str, object]:
    """Return {label, confidence} for a single binary prediction."""
    pred = int(model.predict(row)[0])
    proba = model.predict_proba(row)[0]
    confidence = float(proba[pred])
    return {"label": BINARY_LABELS[pred], "confidence": confidence}


def predict_binary(model_name: str, df_row: pd.DataFrame) -> Dict[str, object]:
    """Predict Benign/Attack for a single (already validated) row.

    ``model_name`` is one of ``random_forest``, ``decision_tree``, ``knn``.
    """
    if model_name not in BINARY_MODELS:
        raise ValueError(f"Unknown binary model: {model_name}")
    models = get_models()
    row = validate_features(df_row)
    if len(row) != 1:
        raise ValueError("predict_binary expects exactly one row.")
    return _binary_row_result(models[model_name], _standardize(row))


def predict_attack_type(df_row: pd.DataFrame) -> Dict[str, object]:
    """Predict the attack category for a single (already validated) row."""
    models = get_models()
    row = validate_features(df_row)
    if len(row) != 1:
        raise ValueError("predict_attack_type expects exactly one row.")
    row = _standardize(row)
    model = models["attack_type"]
    category = str(model.predict(row)[0])
    proba = model.predict_proba(row)[0]
    confidence = float(np.max(proba))
    return {"category": category, "confidence": confidence}


def batch_predict(
    df: pd.DataFrame, model_name: str = "random_forest"
) -> List[Dict[str, object]]:
    """Run the chained pipeline over a full frame.

    Applies the binary model first; rows classified as Attack are then fed
    to the multiclass model. Returns one dict per input row (in order):

    ``{row, label, confidence, category, category_confidence}``
    """
    if model_name not in BINARY_MODELS:
        raise ValueError(f"Unknown binary model: {model_name}")

    df = validate_features(df)
    df = _standardize(df)
    models = get_models()

    binary_model = models[model_name]
    attack_model = models["attack_type"]

    binary_preds = binary_model.predict(df)
    binary_proba = binary_model.predict_proba(df)

    attack_mask = binary_preds == 1
    attack_rows = df[attack_mask]
    attack_proba = attack_model.predict_proba(attack_rows) if attack_rows.shape[0] else None

    results: List[Dict[str, object]] = []
    attack_idx_iter = 0

    for i in range(len(df)):
        pred = int(binary_preds[i])
        label = BINARY_LABELS[pred]
        confidence = float(binary_proba[i][pred])

        if pred == 1:
            category = str(attack_model.classes_[int(np.argmax(attack_proba[attack_idx_iter]))])
            category_confidence = float(np.max(attack_proba[attack_idx_iter]))
            attack_idx_iter += 1
        else:
            category = None
            category_confidence = None

        results.append(
            {
                "row": i,
                "label": label,
                "confidence": round(confidence, 6),
                "category": category,
                "category_confidence": (
                    round(category_confidence, 6)
                    if category_confidence is not None
                    else None
                ),
            }
        )

    return results
