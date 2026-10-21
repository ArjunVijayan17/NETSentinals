import os
from pathlib import Path

# Base directory of the backend package
BASE_DIR = Path(__file__).resolve().parent.parent

# Model artifact paths (relative to project root)
PROJECT_ROOT = BASE_DIR.parent

BINARY_MODELS_DIR = PROJECT_ROOT / "NetSentinel_models"
ATTACK_MODELS_DIR = PROJECT_ROOT / "NetSentinel_attack_models"

MODEL_PATHS = {
    "random_forest":       BINARY_MODELS_DIR / "random_forest.joblib",
    "decision_tree":       BINARY_MODELS_DIR / "decision_tree.joblib",
    "knn":                 BINARY_MODELS_DIR / "k-nearest_neighbors.joblib",
    "attack_type":         ATTACK_MODELS_DIR / "random_forest_attack_type.joblib",
}

# Database
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'netsentinel.db'}")

# API limits
MAX_UPLOAD_BYTES = 50 * 1024 * 1024   # 50 MB
MAX_UPLOAD_ROWS  = 500_000

# CORS
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# The 20 required feature columns (exact names post-strip)
REQUIRED_FEATURES = [
    "Packet Length Variance",
    "Packet Length Std",
    "Bwd Packet Length Std",
    "Average Packet Size",
    "Avg Bwd Segment Size",
    "Destination Port",
    "Fwd IAT Max",
    "Fwd IAT Std",
    "Subflow Bwd Bytes",
    "Fwd Packet Length Max",
    "Flow IAT Std",
    "Init_Win_bytes_backward",
    "Fwd IAT Total",
    "Idle Min",
    "Avg Fwd Segment Size",
    "Total Length of Fwd Packets",
    "Init_Win_bytes_forward",
    "Fwd IAT Mean",
    "Flow IAT Mean",
    "Min Packet Length",
]

# Label mapping
BINARY_LABELS = {0: "Benign", 1: "Attack"}
