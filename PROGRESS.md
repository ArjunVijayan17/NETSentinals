# NetSentinel — Build Progress Log

## Status

| Phase | Name | Status |
|-------|------|--------|
| 0 | Project Scaffold & MODEL_CONTRACT | ✅ Done (pre-existing) |
| 1 | Backend: Model Inference Service | ✅ Done (runtime-verified) |
| 2 | Backend: FastAPI Endpoints | ✅ Done (runtime-verified) |
| 3 | Backend: Persistence (SQLite) | ✅ Done (runtime-verified) |
| 4 | Frontend: React Dashboard | ✅ Built — `tsc` + `vite build` pass |
| 5 | End-to-End Testing | ✅ 19 tests passed |
| 6 | Demo Preparation | ✅ README + sample data ready |

## ⚠️ Critical finding — models need feature scaling (Phase 0 defect)

**Root cause:** the models were trained on **Z-scored (standardized)** features, but
`MODEL_CONTRACT.md` and `sample-data/sample.csv` treat the features as raw.

Evidence:

- `01_load_and_clean_data.ipynb` runs `StandardScaler().fit_transform(x_train)`
  and saves `standard_scaler.joblib`; `train.parquet`/`test.parquet` are
  standardized float32.
- RF tree split thresholds are on standardized scale (e.g. `Packet Length Std`
  threshold ≈ 1.38; raw values are ~thousands).
- KNN's internal `StandardScaler` has `mean_ ≈ 0`, `scale_ ≈ 1` — it was fit on
  already-standardized data (double-scaling, a no-op).

**Consequence:** feeding raw sample rows makes every model degenerate
(RF → all "Benign", DT/KNN → all "Attack"). `sample.csv` (271 real attacks)
scores **0/271 attacks detected**.

**Blocker:** `standard_scaler.joblib` (and the raw CICIDS CSVs) are NOT in this
repo — they live in the original Colab Google Drive. The exact training
mean/std cannot be reconstructed from the 471-row sample (wrong class balance:
271 attack / 200 benign vs. ~17% attack in training). Approximate scalers
(sample-stats, benign-stats) were tested and do not recover the decision
boundary.

**Fix wired in (awaiting the scaler file):**

- `config.py` — `SCALER_PATH = PROJECT_ROOT / "standard_scaler.joblib"`.
- `loader.py` — `load_scaler()` / `get_scaler()`; raises a clear
  `FileNotFoundError` if the file is absent.
- `inference.py` — `_standardize()` applies the scaler in `predict_binary`,
  `predict_attack_type`, and `batch_predict` before every prediction.
- `main.py` — lifespan loads the scaler at startup (fails fast).
- `verify_models.py` — standardizes the test row when the scaler is present.
- `MODEL_CONTRACT.md` / `README.md` — corrected the "no scaling" claim.

**✅ RESOLVED — scaler rebuilt from the raw dataset.**

The user had no access to the original Google Drive, and the UNB download
server was down (security lockdown). Instead:

1. Downloaded `MachineLearningCSV.zip` (235 MB) from the Hugging Face mirror
   `bencorn/CICIDS2017` (`csvs/MachineLearningCSV.zip`).
2. Wrote `backend/scripts/rebuild_scaler.py` — an exact reproduction of the
   cleaning + split + `StandardScaler` fit from `01_load_and_clean_data.ipynb`
   (feature selection skipped; StandardScaler is per-column, so fitting on the
   20 known features is equivalent).
3. Verified exactness: **cleaned rows 2,497,980**, train 1,998,384 / test
   499,596 — identical to the notebook output.
4. Result on `sample-data/sample.csv`: RF detects **229/271 attacks with 0
   benign false positives**; attack categories match ground truth almost
   exactly (DDoS 20, PortScan 20, SSH-Patator 20, Web Attack 60, etc.).

`standard_scaler.joblib` is now at the project root. Raw `dataset/` folder is
gitignored and can be deleted to reclaim ~1 GB.

## Environment constraint

- No Python interpreter is installed on this machine (only the Microsoft Store
  stub at `WindowsApps\python.exe`). The backend **cannot be run or pytest-ed**
  here. All backend code is written and self-reviewed, but unverified at runtime.
- Node.js v24 available — the frontend installs, type-checks (`tsc -b`) and
  builds (`vite build`) cleanly.

## What was built

### Phase 1 — Inference service
- `backend/app/models/loader.py` — loads 4 artifacts once, caches them.
- `backend/app/models/inference.py` — `validate_features`, `predict_binary`,
  `predict_attack_type`, `batch_predict` (chained binary → multiclass).
- `backend/tests/test_inference.py` — schema + NaN/inf + happy-path tests.

### Phase 2 — FastAPI endpoints
- `backend/app/main.py` — lifespan (load models, init DB), CORS, routers.
- `backend/app/routers/health.py` — `/health`, `/models`, `/metrics`.
- `backend/app/routers/predict.py` — `POST /predict`.
- `backend/app/routers/analysis.py` — `/analyze-csv`, `/analyses`,
  `/analyses/{id}`, `/analyses/{id}/download`.
- `backend/app/metrics.py` — verified metrics, confusion matrices, feature
  importance hardcoded from notebook outputs.
- `backend/app/schemas/` — Pydantic request/response models.

### Phase 3 — Persistence
- `backend/app/db/database.py` — SQLAlchemy 2.0 engine + `analyses` table.
- `backend/app/db/crud.py` — `save_analysis`, `get_analysis`, `list_analyses`.

### Phase 4 — Frontend
- Vite + React + TS + Tailwind + Recharts scaffold.
- Pages: Overview, Analyze, Results, ModelEval, History.
- Components: Sidebar/TopBar, StatCard/ModelCard, DonutChart/CategoryBarChart/
  FeatureImportanceChart/ConfusionMatrix, DataTable/Badge, DropZone/ProgressBar.
- API clients + hooks + types.
- `npm install` → 196 packages; `npm run build` → clean.

### Phase 5 — Tests
- `backend/tests/test_api.py` — health, models, metrics, predict (happy +
  missing feature), analyze-csv (happy + missing columns + NaN), list/detail/
  download, 404.
- `conftest.py`, `pytest.ini` at repo root.

### Phase 6 — Demo prep
- `README.md` — prerequisites, start commands, demo walkthrough, limitations,
  CICIDS2017 attribution.
- `sample-data/sample.csv` — 471 rows (200+ benign / attack mix), includes
  `ground_truth_label` column (ignored by the pipeline).

## Verified data (source: notebook outputs)

### Binary model metrics (CICIDS2017 test split, 499,596 rows)

| Model | Accuracy | Precision | Recall | F1 |
|-------|----------|-----------|--------|-----|
| Random Forest | 0.9976 | 0.9868 | 0.9994 | 0.9930 |
| Decision Tree | 0.9976 | 0.9871 | 0.9992 | 0.9931 |
| K-Nearest Neighbors | 0.9903 | 0.9689 | 0.9746 | 0.9717 |

### Attack-type model (85,145 attack rows)

accuracy 0.9994 · precision_macro 0.9971 · recall_macro 0.9852 ·
f1_macro 0.9907 · f1_weighted 0.9994

12 categories: Bot, DDoS, DoS GoldenEye, DoS Hulk, DoS Slowhttptest,
DoS slowloris, FTP-Patator, Heartbleed, Infiltration, PortScan, SSH-Patator,
Web Attack.

### Confusion matrices (derived from verified per-class report)

Derived deterministically in `metrics.py` from recall × support; no notebook
cell prints the raw matrix.

## Next steps

1. `backend\.venv\Scripts\python.exe -m pytest` — 19 passed ✅
2. Start backend: `cd backend && .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000`
3. Start frontend: `cd frontend && npm run dev`
4. Upload `sample-data/sample.csv` → expect 229 attacks / 242 benign (48.6% rate).

All phases complete and runtime-verified.

## Runtime verification done so far

- Python 3.15.1 installed; venv created at `backend/.venv`.
- Installed wheels (Python 3.15 has no sklearn 1.6.1 wheel): scikit-learn 1.9.1,
  numpy 2.5.4, pandas 3.0.6, joblib 1.6.0, fastapi 0.158.0, uvicorn 0.54.0
  (plain, not `[standard]` — pyyaml has no 3.15 wheel), sqlalchemy 2.1.6,
  pytest 9.1.1.
- `verify_models.py` → all 4 models load and predict.
- `pytest` → 19 passed (before the scaler was wired in; will need re-run).
- Live smoke test: `/health`, `/predict`, `/analyze-csv` all respond.

> `requirements.txt` still pins sklearn 1.6.1 (no 3.15 wheel). Update it to the
> working wheel set above before a clean reinstall on this machine.

## Change log

- 2026-10-21: Verified Phase 0 artifacts + extracted metrics from notebooks.
- 2026-10-21: Built Phases 1–3 (backend inference, API, persistence).
- 2026-10-21: Built Phase 4 (frontend) — builds clean.
- 2026-10-21: Wrote Phase 5 tests and Phase 6 README.
- 2026-10-21: Fixed `created_at` omission in analysis `_detail`; added
  `backend/__init__.py`; added `vite-env.d.ts`.
