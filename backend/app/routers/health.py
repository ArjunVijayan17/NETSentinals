"""Health, model listing, and metrics endpoints."""
from __future__ import annotations

from fastapi import APIRouter

from ..config import BINARY_LABELS, REQUIRED_FEATURES
from ..metrics import (
    ATTACK_CLASS_REPORT,
    ATTACK_FEATURE_IMPORTANCE,
    ATTACK_SUMMARY,
    BINARY_FEATURE_IMPORTANCE,
    BINARY_REPORT,
    BINARY_SUMMARY,
    confusion_matrix,
)
from ..models.loader import get_models

router = APIRouter()

MODEL_ROLES = {
    "random_forest": {
        "role": "Primary binary detector (Benign vs Attack)",
        "classes": [BINARY_LABELS[0], BINARY_LABELS[1]],
    },
    "decision_tree": {
        "role": "Comparison binary detector (Benign vs Attack)",
        "classes": [BINARY_LABELS[0], BINARY_LABELS[1]],
    },
    "knn": {
        "role": "Comparison binary detector (Benign vs Attack)",
        "classes": [BINARY_LABELS[0], BINARY_LABELS[1]],
    },
    "attack_type": {
        "role": "Multiclass attack-type classifier (runs on Attack rows only)",
        "classes": [r["class"] for r in ATTACK_CLASS_REPORT],
    },
}


@router.get("/health")
def health():
    models = get_models()
    status = {name: (name in models) for name in MODEL_ROLES}
    return {"status": "ok", "models": status, "features": len(REQUIRED_FEATURES)}


@router.get("/models")
def list_models():
    return [
        {
            "name": name,
            "role": meta["role"],
            "feature_count": len(REQUIRED_FEATURES),
            "classes": meta["classes"],
        }
        for name, meta in MODEL_ROLES.items()
    ]


@router.get("/metrics")
def metrics():
    return {
        "dataset": {
            "name": "CICIDS2017",
            "test_rows": 499596,
            "benign_rows": 414451,
            "attack_rows": 85145,
            "disclaimer": (
                "Metrics are from the CICIDS2017 test split. They are a "
                "snapshot of model performance on that dataset, not a live benchmark."
            ),
        },
        "binary": {
            name: {
                "summary": BINARY_SUMMARY[name],
                "report": BINARY_REPORT[name],
                "confusion_matrix": confusion_matrix(name),
            }
            for name in BINARY_SUMMARY
        },
        "attack_type": {
            "summary": ATTACK_SUMMARY,
            "class_report": ATTACK_CLASS_REPORT,
        },
        "feature_importance": {
            "binary": BINARY_FEATURE_IMPORTANCE,
            "attack_type": ATTACK_FEATURE_IMPORTANCE,
        },
    }
