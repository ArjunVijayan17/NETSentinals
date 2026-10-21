# NetSentinel

Network threat detection and security analytics demo. NetSentinel classifies
uploaded flow records as **Benign** or **Attack** using models trained on the
CICIDS2017 dataset, then predicts the attack category (DDoS, PortScan, Web
Attack, etc.) for detected attacks.

> **Scope:** this is a CSV-analysis demo. The models classify *flow records*
> (already-extracted features). NetSentinel does **not** capture packets or
> monitor live traffic.

## Architecture

- **Backend** — FastAPI + scikit-learn models (`joblib`), SQLite persistence.
- **Frontend** — React + Vite + TypeScript + Tailwind CSS + Recharts.
- **Models** — Random Forest (primary binary), Decision Tree, K-Nearest
  Neighbors (comparison), and a Random Forest attack-type classifier.

The inference contract is documented in [`MODEL_CONTRACT.md`](MODEL_CONTRACT.md).

## Prerequisites

- Python 3.11+
- Node.js 18+ and npm

## Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

- API docs (Swagger): http://localhost:8000/docs
- Health check: http://localhost:8000/health

Model artifacts (`NetSentinel_models/`, `NetSentinel_attack_models/`) must be
present in the **project root** (one level above `backend/`), as referenced by
`backend/app/config.py`.

The **training scaler** (`standard_scaler.joblib`) must also be present at the
project root. The models were trained on Z-scored features, so raw input is
standardized with this scaler before inference. Without it the backend refuses
to start (rather than returning incorrect predictions).

## Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend calls the backend at
`http://localhost:8000` by default; override with `VITE_API_BASE_URL` in
`frontend/.env.local` if needed.

## Demo walkthrough

1. Start the backend, then the frontend.
2. Open the **Overview** page (empty until the first analysis).
3. Go to **Analyze Traffic** and upload `sample-data/sample.csv`.
4. The upload progress bar fills, then a summary card appears.
5. Click **View full results** to see the per-row table, charts, and download
   the prediction CSV.
6. Open **Model Evaluation** for accuracy/precision/recall/F1, confusion
   matrices, and feature importance.
7. Open **History** to see persisted analyses (survive a backend restart).

### Live Monitor demo

The **Live Monitor** page streams flow predictions in real time. Ambient
traffic is replayed from real benign CICIDS rows; click **Simulate Attack** to
inject real attack flows (DDoS, PortScan, etc.) and watch the alert feed and
traffic chart react. This demonstrates attack detection without needing real
malicious traffic on your network.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Model load status |
| GET | `/models` | Model roles and class labels |
| POST | `/predict` | Single-row JSON prediction |
| POST | `/analyze-csv` | Multipart CSV upload → batch analysis |
| GET | `/analyses` | List past analyses |
| GET | `/analyses/{id}` | Full analysis with row results |
| GET | `/analyses/{id}/download` | Download prediction CSV |
| GET | `/metrics` | Verified evaluation metrics |
| GET | `/live/stream` | Server-Sent Events stream of live flow predictions |
| POST | `/live/simulate` | Inject simulated attack flows into the live stream |

## Testing

```bash
# from the project root (backend venv active)
pytest
```

The suite covers inference (happy path, missing columns, NaN/inf) and API
endpoints (predict, analyze-csv, persistence, 404).

## Known limitations

- **sklearn version warning:** models were serialized with scikit-learn
  `1.6.1`. A newer runtime prints an `InconsistentVersionWarning` on load;
  inference is unaffected. `requirements.txt` pins `scikit-learn==1.6.1`.
- **Confidence is a model score**, not a guaranteed attack probability.
- Metrics reflect the CICIDS2017 test split (499,596 rows), not live traffic.
- Works fully offline; no external API calls.

## Attribution

- **Dataset:** CICIDS2017, Canadian Institute for Cybersecurity (University of
  New Brunswick). Used for model training and evaluation.
- **Models:** trained via the notebooks in `notebooks/` (scikit-learn).
- This application was implemented independently; it does not reuse the
  reference repository's application code.
