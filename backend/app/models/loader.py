"""Model loading — load all four artifacts once and cache them."""
from __future__ import annotations

import warnings
from typing import Dict

import joblib

from ..config import MODEL_PATHS, SCALER_PATH

# Models were serialized with scikit-learn 1.6.1; a newer runtime emits a
# harmless InconsistentVersionWarning on load. Inference is unaffected.
warnings.filterwarnings("ignore", category=UserWarning)

_cache: Dict[str, object] = {}
_scaler = None


def load_models() -> Dict[str, object]:
    """Load every model artifact once and return them keyed by role name.

    Roles: ``random_forest``, ``decision_tree``, ``knn``, ``attack_type``.
    """
    global _cache
    if _cache:
        return _cache

    for name, path in MODEL_PATHS.items():
        if not path.exists():
            raise FileNotFoundError(f"Model artifact not found: {path}")
        _cache[name] = joblib.load(path)

    return _cache


def get_models() -> Dict[str, object]:
    """Return the cached model dict, loading on first call."""
    return load_models()


def load_scaler():
    """Load the training StandardScaler (required for correct inference)."""
    global _scaler
    if _scaler is not None:
        return _scaler

    if not SCALER_PATH.exists():
        raise FileNotFoundError(
            "Training scaler not found: "
            f"{SCALER_PATH}. The models were trained on standardized "
            "features, so raw input cannot be classified without it. "
            "Place the original standard_scaler.joblib at this path."
        )

    _scaler = joblib.load(SCALER_PATH)
    return _scaler


def get_scaler():
    """Return the cached scaler, loading on first call."""
    return load_scaler()
