"""Unit tests for the inference service (Phase 1)."""
import numpy as np
import pandas as pd
import pytest

from backend.app.config import REQUIRED_FEATURES
from backend.app.models.inference import (
    batch_predict,
    predict_attack_type,
    predict_binary,
    validate_features,
)


@pytest.fixture(scope="module")
def sample_row() -> pd.DataFrame:
    """One plausible, fully-populated feature row."""
    values = {
        "Packet Length Variance": 1000.0,
        "Packet Length Std": 31.6,
        "Bwd Packet Length Std": 20.0,
        "Average Packet Size": 150.0,
        "Avg Bwd Segment Size": 120.0,
        "Destination Port": 80.0,
        "Fwd IAT Max": 500000.0,
        "Fwd IAT Std": 200000.0,
        "Subflow Bwd Bytes": 300.0,
        "Fwd Packet Length Max": 400.0,
        "Flow IAT Std": 300000.0,
        "Init_Win_bytes_backward": 65535.0,
        "Fwd IAT Total": 1000000.0,
        "Idle Min": 0.0,
        "Avg Fwd Segment Size": 150.0,
        "Total Length of Fwd Packets": 600.0,
        "Init_Win_bytes_forward": 65535.0,
        "Fwd IAT Mean": 250000.0,
        "Flow IAT Mean": 200000.0,
        "Min Packet Length": 40.0,
    }
    return pd.DataFrame([values])[REQUIRED_FEATURES]


def test_validate_features_returns_exact_order(sample_row):
    out = validate_features(sample_row)
    assert list(out.columns) == REQUIRED_FEATURES


def test_validate_features_strips_whitespace():
    df = pd.DataFrame(
        [[1.0] * 20],
        columns=[f" {c}" for c in REQUIRED_FEATURES],
    )
    out = validate_features(df)
    assert list(out.columns) == REQUIRED_FEATURES


def test_validate_features_rejects_missing_columns():
    df = pd.DataFrame([[1.0]], columns=["Destination Port"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_features(df)


def test_validate_features_rejects_nan():
    df = pd.DataFrame([[np.nan] * 20], columns=REQUIRED_FEATURES)
    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_features(df)


def test_validate_features_rejects_inf():
    df = pd.DataFrame([[np.inf] * 20], columns=REQUIRED_FEATURES)
    with pytest.raises(ValueError, match="NaN or infinite"):
        validate_features(df)


def test_predict_binary_returns_expected_shape(sample_row):
    for name in ("random_forest", "decision_tree", "knn"):
        result = predict_binary(name, sample_row)
        assert result["label"] in ("Benign", "Attack")
        assert 0.0 <= result["confidence"] <= 1.0


def test_predict_binary_rejects_unknown_model(sample_row):
    with pytest.raises(ValueError, match="Unknown binary model"):
        predict_binary("nope", sample_row)


def test_predict_attack_type(sample_row):
    result = predict_attack_type(sample_row)
    assert isinstance(result["category"], str)
    assert 0.0 <= result["confidence"] <= 1.0


def test_batch_predict_chains_multiclass(sample_row):
    rows = pd.concat([sample_row] * 3, ignore_index=True)
    results = batch_predict(rows, model_name="random_forest")
    assert len(results) == 3
    for r in results:
        assert r["label"] in ("Benign", "Attack")
        if r["label"] == "Attack":
            assert r["category"] is not None
            assert r["category_confidence"] is not None
        else:
            assert r["category"] is None
