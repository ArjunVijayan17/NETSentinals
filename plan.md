# NetSentinel — Implementation Plan

> Based on: `NetSentinel_Project_Handoff.md` + live inspection of model artifacts.

---

## Verified Artifact Inventory

All models are confirmed present and loadable. **Note:** models were trained with sklearn 1.6.1; current env is 1.9.0. Inference works but retrain if instability is observed.

### Binary Models (`NetSentinel_models/`)

| File | Type | Classes | Features | Notes |
|------|------|---------|----------|-------|
| `random_forest.joblib` | `RandomForestClassifier` | `[0, 1]` | 20 | Primary detector; supports `predict_proba` |
| `decision_tree.joblib` | `DecisionTreeClassifier` | `[0, 1]` | 20 | Baseline; supports `predict_proba` |
| `k-nearest_neighbors.joblib` | `Pipeline(StandardScaler → KNN)` | `[0, 1]` | 20 | Includes scaler internally; supports `predict_proba` |

### Multiclass Model (`NetSentinel_attack_models/`)

| File | Type | Classes | Features |
|------|------|---------|----------|
| `random_forest_attack_type.joblib` | `RandomForestClassifier` | 12 attack types (see below) | 20 (same as binary) |

**Attack categories:** `Bot`, `DDoS`, `DoS GoldenEye`, `DoS Hulk`, `DoS Slowhttptest`, `DoS slowloris`, `FTP-Patator`, `Heartbleed`, `Infiltration`, `PortScan`, `SSH-Patator`, `Web Attack`

### The 20 Shared Features (exact names, exact order)

```python
FEATURES = [
    "Packet Length Variance", "Packet Length Std", "Bwd Packet Length Std",
    "Average Packet Size", "Avg Bwd Segment Size", "Destination Port",
    "Fwd IAT Max", "Fwd IAT Std", "Subflow Bwd Bytes",
    "Fwd Packet Length Max", "Flow IAT Std", "Init_Win_bytes_backward",
    "Fwd IAT Total", "Idle Min", "Avg Fwd Segment Size",
    "Total Length of Fwd Packets", "Init_Win_bytes_forward",
    "Fwd IAT Mean", "Flow IAT Mean", "Min Packet Length"
]
```

> **Key finding:** All 4 models share the exact same 20 features. Binary and multiclass models can be chained directly. KNN includes its own `StandardScaler` in the pipeline — no separate scaler file is needed.

---

## Project Structure

```text
NetSentinel/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + CORS + lifespan
│   │   ├── models/               # Model loading/inference service
│   │   │   ├── loader.py
│   │   │   └── inference.py
│   │   ├── routers/
│   │   │   ├── health.py
│   │   │   ├── predict.py
│   │   │   └── analysis.py
│   │   ├── schemas/
│   │   │   ├── predict.py
│   │   │   └── analysis.py
│   │   ├── db/
│   │   │   ├── database.py       # SQLite (SQLAlchemy)
│   │   │   └── crud.py
│   │   └── config.py
│   ├── artifacts/                # Symlink or copy of model .joblib files
│   │   ├── binary/               → ../NetSentinel_models/
│   │   └── attack_type/          → ../NetSentinel_attack_models/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                # Overview, Analyze, Results, Models, History
│   │   ├── components/
│   │   ├── api/                  # axios/fetch wrappers
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── sample-data/                  # Small curated CSV for demo
├── MODEL_CONTRACT.md             # Feature/label/preprocessing spec
├── plan.md                       # This file
└── README.md
```

---

## Implementation Phases

### Phase 0 — Project Scaffold & MODEL_CONTRACT ✅ (ready to start)

**Goal:** Get the skeleton in place and document the inference contract before writing a single endpoint.

- [ ] Write `MODEL_CONTRACT.md` with confirmed feature list, label mapping (`0=Benign`, `1=Attack`), model paths, pipeline notes (KNN self-scales, RF/DT do not scale), and probability support.
- [ ] Scaffold `backend/` with `requirements.txt` (`fastapi`, `uvicorn`, `scikit-learn==1.6.1`, `joblib`, `pandas`, `pydantic`, `sqlalchemy`, `python-multipart`, `aiofiles`).
- [ ] Scaffold `frontend/` with Vite + React + TypeScript + Tailwind CSS.
- [ ] Create `sample-data/sample.csv` by slicing a representative mix (~200 rows benign + ~50 rows attack) from the CICIDS CSVs — renaming columns to the exact 20 feature names.
- [ ] Run a quick sanity-check script (`backend/scripts/verify_models.py`) to load all 4 models and run a prediction on one row; print class and probability.

---

### Phase 1 — Backend: Model Inference Service

**Goal:** Isolated, tested inference layer — no HTTP yet.

- [ ] `backend/app/models/loader.py` — load all 4 `.joblib` files once at startup; expose a dict of named model objects.
- [ ] `backend/app/models/inference.py` — functions:
  - `predict_binary(model_name, df_row) → {label: "Benign"|"Attack", confidence: float}`
  - `predict_attack_type(df_row) → {category: str, confidence: float}`
  - `batch_predict(df) → list[dict]` — applies binary RF first; for attack rows runs multiclass.
  - `validate_features(df)` — raises if required columns are missing or NaN/inf present.
- [ ] Unit tests in `backend/tests/test_inference.py` using a known row from the test CSV.

---

### Phase 2 — Backend: FastAPI Endpoints

**Goal:** Working REST API with Swagger docs.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Returns model load status for all 4 models |
| GET | `/models` | Lists models, roles, feature count, class labels |
| POST | `/predict` | Single-row JSON prediction (exact 20 features) |
| POST | `/analyze-csv` | Multipart CSV upload → batch analysis → persisted result |
| GET | `/analyses` | List past analysis sessions (id, filename, timestamp, counts) |
| GET | `/analyses/{id}` | Full analysis: summary + per-row results |
| GET | `/analyses/{id}/download` | Download prediction CSV |
| GET | `/metrics` | Hardcoded verified training metrics from notebook outputs |

**Implementation notes:**
- Use `lifespan` context manager to load models once on startup.
- Pydantic `BaseModel` for all request/response schemas.
- CSV limits: max 50 MB / 500,000 rows; raise `422` with a clear message if exceeded.
- Strip whitespace from column names on CSV parse (CICIDS CSVs have leading spaces).
- CORS: allow `http://localhost:5173` in dev.
- Use `BackgroundTasks` or async to avoid blocking on large CSVs.

---

### Phase 3 — Backend: Persistence (SQLite)

**Goal:** Analyses survive backend restarts.

Schema (SQLAlchemy / SQLite):

```sql
analyses (
    id           TEXT PRIMARY KEY,   -- UUID
    filename     TEXT,
    created_at   DATETIME,
    total_rows   INTEGER,
    benign_count INTEGER,
    attack_count INTEGER,
    attack_rate  REAL,
    categories   TEXT,              -- JSON string of {category: count}
    model_name   TEXT,
    row_results  TEXT               -- JSON string of list[{row, label, category, conf}]
)
```

- [ ] `backend/app/db/database.py` — SQLAlchemy engine + session factory.
- [ ] `backend/app/db/crud.py` — `save_analysis()`, `get_analysis()`, `list_analyses()`.
- [ ] Alembic migrations (optional for demo; `create_all()` is fine for SQLite).

---

### Phase 4 — Frontend: React Dashboard

**Goal:** Polished dark-theme security dashboard.

**Design direction:** Dark background (`#0f1117`), accent color teal/cyan (`#00d4aa`), attack color red (`#ef4444`), benign color green (`#22c55e`). Recharts for all charts. Clean sans-serif typography.

#### Pages

1. **Overview** (`/`)
   - Stats cards: Total Analyzed, Attack Rate %, Benign Count, Attack Count.
   - Donut chart: Benign vs Attack.
   - Bar chart: Attack categories.
   - Recent analyses table (last 5 sessions).

2. **Analyze Traffic** (`/analyze`)
   - Drag-and-drop CSV upload zone.
   - Column validation preview: shows whether required features are found.
   - Progress bar during analysis.
   - Results summary card on completion with link to full results.
   - Download button for prediction CSV.

3. **Detection Results** (`/analyses/:id`)
   - Summary cards (reuse Overview stats).
   - Searchable/sortable table: Row #, Label (colored badge), Attack Category, Confidence %.
   - Pagination (50 rows per page).

4. **Model Evaluation** (`/models`)
   - Cards for each model: accuracy, precision, recall, F1.
   - Confusion matrix heatmap per model.
   - Feature importance bar chart (RF models).
   - Clear disclaimer: metrics from CICIDS2017 test split; not a live benchmark.

5. **Analysis History** (`/history`)
   - Table of all past analyses with filename, date, total rows, attack rate.
   - Click to navigate to Detection Results.

#### Component structure

```
src/
├── pages/         Overview.tsx, Analyze.tsx, Results.tsx, ModelEval.tsx, History.tsx
├── components/
│   ├── Layout/    Sidebar.tsx, TopBar.tsx
│   ├── Charts/    DonutChart.tsx, BarChart.tsx, ConfusionMatrix.tsx
│   ├── Cards/     StatCard.tsx, ModelCard.tsx
│   ├── Table/     DataTable.tsx, Badge.tsx
│   └── Upload/    DropZone.tsx, ProgressBar.tsx
├── api/           client.ts (axios), analyses.ts, models.ts
├── hooks/         useAnalysis.ts, useModels.ts
└── types/         analysis.ts, model.ts
```

---

### Phase 5 — End-to-End Testing

- [ ] Backend: `pytest` suite covering happy path, missing columns, NaN values, oversized file.
- [ ] Frontend: Manual walkthrough with `sample-data/sample.csv`.
- [ ] Verify chart counts match API response counts.
- [ ] Restart backend → history persists.
- [ ] Test with a deliberately malformed CSV.
- [ ] Test `/predict` single-row via Swagger UI.

---

### Phase 6 — Demo Preparation

- [ ] Finalize `sample-data/sample.csv` (200 benign + 50 attack rows, labeled for ground truth comparison).
- [ ] Write `README.md` with: prerequisites, `uvicorn` start command, `npm run dev` start command, demo walkthrough steps.
- [ ] Document sklearn version warning and its impact.
- [ ] Add attribution: CICIDS2017 dataset (Canadian Institute for Cybersecurity), model training workflow.
- [ ] Verify the full demo works offline (no external API calls).

---

## Known Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| sklearn 1.6.1 → 1.9.0 version mismatch warnings | Test inference thoroughly; pin `scikit-learn==1.6.1` in `requirements.txt` |
| KNN is a Pipeline, RF/DT are plain estimators | `inference.py` handles both via duck-typing / `isinstance` check |
| CICIDS CSVs have leading spaces in column names | `df.columns = df.columns.str.strip()` on every upload |
| Large CSV uploads blocking event loop | Use `asyncio.to_thread` or `BackgroundTasks` for heavy pandas work |
| No scaler file for RF/DT (KNN has its own) | Confirmed: RF and DT do not require external scaling (tree-based) |

---

## Immediate Next Steps (Start Here)

1. **`MODEL_CONTRACT.md`** — codify the inference contract from the verified facts above.
2. **Backend scaffold** — `requirements.txt`, `app/main.py`, folder structure.
3. **`verify_models.py`** script — confirm all 4 models predict correctly on one row.
4. **`inference.py`** — the core service layer used by all endpoints.
5. **FastAPI endpoints** — starting with `/health` and `/predict`, then `/analyze-csv`.
6. **Frontend scaffold** — Vite + React + Tailwind, then page by page.
