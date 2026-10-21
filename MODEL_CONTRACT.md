# NetSentinel — Model Contract

This document is the single source of truth for inference against all trained models.
**Do not fabricate or alter any value here.** All facts were verified by direct inspection of the `.joblib` files.

---

## 1. Input Feature Schema

All four models accept **exactly the same 20 features**, in this exact order:

| # | Feature Name | Notes |
|---|--------------|-------|
| 1 | `Packet Length Variance` | |
| 2 | `Packet Length Std` | |
| 3 | `Bwd Packet Length Std` | |
| 4 | `Average Packet Size` | |
| 5 | `Avg Bwd Segment Size` | |
| 6 | `Destination Port` | |
| 7 | `Fwd IAT Max` | |
| 8 | `Fwd IAT Std` | |
| 9 | `Subflow Bwd Bytes` | |
| 10 | `Fwd Packet Length Max` | |
| 11 | `Flow IAT Std` | |
| 12 | `Init_Win_bytes_backward` | |
| 13 | `Fwd IAT Total` | |
| 14 | `Idle Min` | |
| 15 | `Avg Fwd Segment Size` | |
| 16 | `Total Length of Fwd Packets` | |
| 17 | `Init_Win_bytes_forward` | |
| 18 | `Fwd IAT Mean` | |
| 19 | `Flow IAT Mean` | |
| 20 | `Min Packet Length` | |

> **Important:** CICIDS2017 CSV files often have a **leading space** in column names (e.g., `" Packet Length Variance"`).
> Always strip whitespace from column names before passing to models: `df.columns = df.columns.str.strip()`

---

## 2. Preprocessing Requirements

| Model | Requires External Scaler? | Notes |
|-------|--------------------------|-------|
| `random_forest.joblib` | ❌ No | Tree-based; scale-invariant |
| `decision_tree.joblib` | ❌ No | Tree-based; scale-invariant |
| `k-nearest_neighbors.joblib` | ❌ No (self-contained) | **Is a `Pipeline`**: `StandardScaler → KNeighborsClassifier`. Scaling is applied internally. |
| `random_forest_attack_type.joblib` | ❌ No | Tree-based; scale-invariant |

**No external scaler file is needed.** The KNN model handles its own scaling.

---

## 3. Model Artifacts

| Role | File Path | sklearn Type | sklearn Version |
|------|-----------|-------------|-----------------|
| Primary binary detector | `NetSentinel_models/random_forest.joblib` | `RandomForestClassifier` | 1.6.1 |
| Comparison binary detector | `NetSentinel_models/decision_tree.joblib` | `DecisionTreeClassifier` | 1.6.1 |
| Comparison binary detector | `NetSentinel_models/k-nearest_neighbors.joblib` | `Pipeline(StandardScaler, KNeighborsClassifier)` | 1.6.1 |
| Attack type classifier | `NetSentinel_attack_models/random_forest_attack_type.joblib` | `RandomForestClassifier` | 1.6.1 |

> **sklearn version note:** Models were serialized with sklearn `1.6.1`. The runtime environment uses `1.9.0`.
> A `InconsistentVersionWarning` will appear on load — this is expected. Inference is functional but
> pinning `scikit-learn==1.6.1` in `requirements.txt` is strongly recommended to eliminate this risk.

---

## 4. Binary Model Output

**Classes:** `[0, 1]`

| Class Value | Label | Meaning |
|-------------|-------|---------|
| `0` | `Benign` | Normal traffic |
| `1` | `Attack` | Malicious traffic |

- `model.predict(X)` → `array([0, 1, 0, ...])` — integer class per row
- `model.predict_proba(X)` → `array([[p_benign, p_attack], ...])` — confidence scores
  - Report `predict_proba[:, 1]` as **attack confidence** (probability of being an attack)
  - For the KNN Pipeline, `predict_proba` is forwarded to the final estimator step automatically

---

## 5. Multiclass Attack Type Output

**Classes (12 total):** verified from `random_forest_attack_type.classes_`

```
['Bot', 'DDoS', 'DoS GoldenEye', 'DoS Hulk', 'DoS Slowhttptest',
 'DoS slowloris', 'FTP-Patator', 'Heartbleed', 'Infiltration',
 'PortScan', 'SSH-Patator', 'Web Attack']
```

- `model.predict(X)` → string class name per row
- `model.predict_proba(X)` → probability per class; report `max` as confidence
- **Only run the multiclass model on rows that the binary model classified as `Attack (1)`.**

---

## 6. Inference Pipeline (Chained)

```
Input CSV
    │
    ▼
strip column whitespace
validate all 20 features present
drop/reject rows with NaN or Inf
    │
    ▼
Binary RF predict(X[20 features])
    ├── 0 (Benign) ──► label="Benign", category=null, confidence=proba[:, 0]
    └── 1 (Attack) ──► label="Attack", confidence=proba[:, 1]
                           │
                           ▼
               Multiclass RF predict(X[same 20 features])
                           │
                           ▼
                      category="DDoS" (etc.), category_confidence=max(proba)
```

---

## 7. Validation Rules (enforced before inference)

1. All 20 feature columns must be present (after stripping whitespace).
2. No `NaN` or `Inf` values allowed — drop or reject those rows.
3. All feature columns must be numeric.
4. Do not reorder, drop, or add columns before passing to the model.
5. Uploaded CSVs: max **50 MB**, max **500,000 rows**.

---

## 8. What NOT to Do

- ❌ Do not re-fit or re-scale features at inference time.
- ❌ Do not invent feature names, class names, or thresholds.
- ❌ Do not run the multiclass model on benign rows.
- ❌ Do not load `.joblib` files from untrusted external sources (they can execute arbitrary code).
- ❌ Do not report `predict_proba` as a guaranteed attack probability — report it as a "model confidence score".
