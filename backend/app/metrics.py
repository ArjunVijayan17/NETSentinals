"""Verified evaluation metrics — hardcoded from notebook outputs.

Source notebooks: ``03_train_models.ipynb``, ``04_attack_type_classification.ipynb``,
``05_model_explainability.ipynb``, ``06_verify_trained_models.ipynb``.

These values describe the CICIDS2017 test split (499,596 rows; 414,451 benign,
85,145 attack). They are a snapshot of model performance on that dataset, not a
live benchmark.
"""
from __future__ import annotations

from typing import Dict, List

# ---------------------------------------------------------------------------
# Binary models: per-class classification report (verified from notebook text)
# ---------------------------------------------------------------------------

BINARY_REPORT: Dict[str, Dict[str, Dict[str, float]]] = {
    "random_forest": {
        "Benign": {"precision": 0.9999, "recall": 0.9973, "f1": 0.9986, "support": 414451},
        "Attack": {"precision": 0.9868, "recall": 0.9994, "f1": 0.9930, "support": 85145},
    },
    "decision_tree": {
        "Benign": {"precision": 0.9998, "recall": 0.9973, "f1": 0.9986, "support": 414451},
        "Attack": {"precision": 0.9871, "recall": 0.9992, "f1": 0.9931, "support": 85145},
    },
    "knn": {
        "Benign": {"precision": 0.9948, "recall": 0.9936, "f1": 0.9942, "support": 414451},
        "Attack": {"precision": 0.9689, "recall": 0.9746, "f1": 0.9717, "support": 85145},
    },
}

# Summary metrics (the comparison table reports the Attack-class precision,
# recall, and F1 alongside overall accuracy).
BINARY_SUMMARY: Dict[str, Dict[str, float]] = {
    "random_forest": {"accuracy": 0.9976, "precision": 0.9868, "recall": 0.9994, "f1": 0.9930},
    "decision_tree": {"accuracy": 0.9976, "precision": 0.9871, "recall": 0.9992, "f1": 0.9931},
    "knn": {"accuracy": 0.9903, "precision": 0.9689, "recall": 0.9746, "f1": 0.9717},
}

# ---------------------------------------------------------------------------
# Multiclass attack-type model
# ---------------------------------------------------------------------------

ATTACK_SUMMARY: Dict[str, float] = {
    "accuracy": 0.9994,
    "precision_macro": 0.9971,
    "recall_macro": 0.9852,
    "f1_macro": 0.9907,
    "f1_weighted": 0.9994,
    "support": 85145,
}

ATTACK_CLASS_REPORT: List[Dict[str, float]] = [
    {"class": "Bot", "precision": 0.9974, "recall": 1.0000, "f1": 0.9987, "support": 390},
    {"class": "DDoS", "precision": 1.0000, "recall": 0.9999, "f1": 0.9999, "support": 25603},
    {"class": "DoS GoldenEye", "precision": 0.9961, "recall": 0.9971, "f1": 0.9966, "support": 2056},
    {"class": "DoS Hulk", "precision": 0.9995, "recall": 0.9999, "f1": 0.9997, "support": 34569},
    {"class": "DoS Slowhttptest", "precision": 0.9943, "recall": 0.9924, "f1": 0.9933, "support": 1046},
    {"class": "DoS slowloris", "precision": 0.9925, "recall": 0.9907, "f1": 0.9916, "support": 1075},
    {"class": "FTP-Patator", "precision": 1.0000, "recall": 1.0000, "f1": 1.0000, "support": 1186},
    {"class": "Heartbleed", "precision": 1.0000, "recall": 1.0000, "f1": 1.0000, "support": 2},
    {"class": "Infiltration", "precision": 1.0000, "recall": 0.8571, "f1": 0.9231, "support": 7},
    {"class": "PortScan", "precision": 0.9998, "recall": 0.9994, "f1": 0.9996, "support": 18139},
    {"class": "SSH-Patator", "precision": 1.0000, "recall": 1.0000, "f1": 1.0000, "support": 644},
    {"class": "Web Attack", "precision": 0.9860, "recall": 0.9860, "f1": 0.9860, "support": 428},
]

# ---------------------------------------------------------------------------
# Feature importance (tree importance, verified from 05_model_explainability)
# ---------------------------------------------------------------------------

BINARY_FEATURE_IMPORTANCE: List[Dict[str, float]] = [
    {"feature": "Average Packet Size", "importance": 0.12020},
    {"feature": "Packet Length Variance", "importance": 0.11610},
    {"feature": "Bwd Packet Length Std", "importance": 0.10306},
    {"feature": "Packet Length Std", "importance": 0.09984},
    {"feature": "Destination Port", "importance": 0.08390},
    {"feature": "Subflow Bwd Bytes", "importance": 0.06770},
    {"feature": "Avg Bwd Segment Size", "importance": 0.06732},
    {"feature": "Init_Win_bytes_backward", "importance": 0.05368},
    {"feature": "Init_Win_bytes_forward", "importance": 0.04243},
    {"feature": "Avg Fwd Segment Size", "importance": 0.04221},
    {"feature": "Fwd Packet Length Max", "importance": 0.04191},
    {"feature": "Total Length of Fwd Packets", "importance": 0.03829},
    {"feature": "Min Packet Length", "importance": 0.02226},
    {"feature": "Fwd IAT Max", "importance": 0.02208},
    {"feature": "Fwd IAT Std", "importance": 0.02045},
    {"feature": "Flow IAT Std", "importance": 0.01520},
    {"feature": "Flow IAT Mean", "importance": 0.01511},
    {"feature": "Fwd IAT Mean", "importance": 0.01484},
    {"feature": "Fwd IAT Total", "importance": 0.01063},
    {"feature": "Idle Min", "importance": 0.00280},
]

ATTACK_FEATURE_IMPORTANCE: List[Dict[str, float]] = [
    {"feature": "Destination Port", "importance": 0.12286},
    {"feature": "Init_Win_bytes_backward", "importance": 0.08633},
    {"feature": "Fwd Packet Length Max", "importance": 0.07741},
    {"feature": "Avg Bwd Segment Size", "importance": 0.06626},
    {"feature": "Subflow Bwd Bytes", "importance": 0.05931},
    {"feature": "Average Packet Size", "importance": 0.05384},
    {"feature": "Fwd IAT Total", "importance": 0.05254},
    {"feature": "Flow IAT Mean", "importance": 0.05122},
    {"feature": "Fwd IAT Mean", "importance": 0.04570},
    {"feature": "Total Length of Fwd Packets", "importance": 0.04550},
    {"feature": "Avg Fwd Segment Size", "importance": 0.04496},
    {"feature": "Flow IAT Std", "importance": 0.04039},
    {"feature": "Fwd IAT Max", "importance": 0.04025},
    {"feature": "Packet Length Variance", "importance": 0.04000},
    {"feature": "Packet Length Std", "importance": 0.03745},
    {"feature": "Init_Win_bytes_forward", "importance": 0.03520},
    {"feature": "Bwd Packet Length Std", "importance": 0.03360},
    {"feature": "Fwd IAT Std", "importance": 0.03231},
    {"feature": "Idle Min", "importance": 0.01989},
    {"feature": "Min Packet Length", "importance": 0.01498},
]


def confusion_matrix(model_name: str) -> Dict[str, List[int]]:
    """Derive the 2x2 confusion matrix from the verified classification report.

    Uses recall and support to recover counts exactly; derived from verified
    notebook values (no notebook cell prints the raw matrix).

    Layout: rows = actual class, columns = predicted class, order [Benign, Attack].
    """
    report = BINARY_REPORT[model_name]

    tp = round(report["Attack"]["recall"] * report["Attack"]["support"])
    fn = int(report["Attack"]["support"]) - tp
    tn = round(report["Benign"]["recall"] * report["Benign"]["support"])
    fp = int(report["Benign"]["support"]) - tn

    return {
        "labels": ["Benign", "Attack"],
        "matrix": [[tn, fp], [fn, tp]],
    }
