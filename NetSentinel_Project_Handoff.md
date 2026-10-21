# NetSentinel — Project Handoff and Implementation Plan

## 1. Project Overview

**Project name:** NetSentinel  
**Goal:** Build an intelligent network threat detection and security analytics application using machine-learning models trained on the CICIDS2017 network traffic dataset.

NetSentinel will analyze network-flow records and predict whether traffic appears benign or malicious. For records classified as attacks, a multiclass model may also predict an attack category. A dashboard will present analysis results, trends, and model evaluation metrics.

**Important scope decision:** The initial expo/demo version should analyze uploaded CSV files. Live network monitoring is out of scope for the first version because it requires separate traffic capture and flow-feature extraction.

This is an independent application. A GitHub repository was used as a reference for training workflows and obtaining model artifacts; NetSentinel's backend, API, dashboard, and application design will be implemented separately. Review the original repository's license and attribution requirements before reusing any of its code or artifacts.

---

## 2. Work Completed So Far

### Dataset and preprocessing

- Downloaded the CICIDS2017 `MachineLearningCSV.zip` dataset.
- Extracted the dataset into CSV files for the days represented in the dataset.
- Ran the preprocessing notebook (`01_load_and_clean_data.ipynb`).
- Processed training and test data into Parquet files.
- Generated feature-selection artifacts.

Known files from the preprocessing workflow:

```text
/content/dataset/processed/
├── train.parquet
├── test.parquet
├── standard_scaler.joblib
└── preprocessing_report.json

/content/artifacts/feature_selection/
├── selected_features.json
├── feature_scores.csv
├── feature_correlation.csv
├── selected_feature_correlation.png
└── top_features.png
```

The files were backed up from Colab to Google Drive under:

```text
/content/drive/MyDrive/NetSentinel/
├── artifacts/
└── dataset/processed/
```

The binary dataset snapshot previously reported these sizes and labels:

- Training rows: 300,000
- Test rows: 499,596
- Training labels: 248,872 Benign and 51,128 Attack
- Test labels: 414,451 Benign and 85,145 Attack

These counts describe the binary dataset snapshot reported during the workflow. Verify them against the actual current files before relying on them.

### Feature selection

- Notebook `02_feature_selection.ipynb` was adjusted to read feature-selection outputs from `/content/artifacts/feature_selection/`.
- The intended selected feature list is in `selected_features.json`.
- A backup/restore workflow was established for moving artifacts between separate Colab runtimes.

### Model training notebooks

The following notebooks have been used or prepared:

- `03_train_models.ipynb` — intended to train binary intrusion-detection models.
- `04_attack_type_classification.ipynb` — intended to train a multiclass attack-type classifier.

The intended binary models are:

1. Random Forest — primary Benign vs. Attack detector.
2. Decision Tree — comparison model.
3. K-Nearest Neighbors (KNN) — comparison model.

The multiclass model is intended to predict the attack category from the available class labels.

**Verification status:** Do not assume all training runs completed successfully or all model files were downloaded. Confirm by inspecting the actual notebook outputs, model output directories, and downloaded ZIP contents.

The binary model artifacts were expected under `artifacts/models/`. The multiclass notebook was configured to save outputs under `artifacts/attack_type_model/`. These paths must be checked against the final notebooks and actual output files.

### Planned stack and architecture

The current proposed stack is:

- **Frontend:** React + Vite + Tailwind CSS
- **Backend:** Python + FastAPI
- **Database:** PostgreSQL (SQLite is acceptable for a quick local prototype)
- **Model artifacts:** `joblib` files plus the exact feature list, preprocessing requirements, and label mapping
- **Initial input mode:** CSV upload
- **Potential later extension:** Live traffic capture and feature extraction, only after the CSV-based version works reliably

---

## 3. Model Responsibilities

| Model | Intended responsibility |
|---|---|
| Random Forest | Primary binary classification: Benign vs. Attack |
| Decision Tree | Baseline/comparison binary classifier |
| KNN | Baseline/comparison binary classifier |
| Multiclass classifier | Predict the attack category for records represented by the training labels |

The first three binary classifiers do not all need to run on every prediction. Use Random Forest as the main detector initially and optionally add a model-comparison page. The multiclass classifier can provide a category prediction for records detected as attacks, provided the model's input features and labels are compatible.

**Critical implementation requirement:** Inspect each trained model and notebook before building inference. Confirm:
- exact input feature names and order;
- whether scaling or other preprocessing is required;
- target labels and class mapping;
- whether the multiclass model uses the same feature set as the binary model;
- whether the saved object is a plain estimator or an sklearn Pipeline;
- how probabilities/confidence values are produced, if supported.

Never invent feature names, class names, thresholds, or output mappings.

---

## 4. Next Steps — Recommended Order

### Phase 1: Verify and organize model artifacts

Before writing the API:

1. Locate the downloaded model ZIP files.
2. Extract them into the project's `backend/models/` directory.
3. Inspect the contents and filenames.
4. Locate `selected_features.json`, the scaler (if required), the multiclass label mapping (if present), and any other preprocessing artifacts.
5. Compare these files against the training notebooks to determine the exact inference contract.
6. Run a small test prediction using a known row from the test dataset and verify that the result is consistent with the notebook.

Suggested local structure:

```text
netsentinel/
├── backend/
│   ├── app/
│   ├── models/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
├── sample-data/
├── README.md
└── docker-compose.yml
```

Do not commit large models, private traffic data, or secrets to a public repository. Use Git LFS or external artifact storage if needed, and check the repository's license and the model/data licenses.

### Phase 2: Build the FastAPI backend

Build the backend before designing the frontend. Load model files once at application startup rather than on every request.

Suggested endpoints:

- `GET /health` — API health and model-loading status.
- `GET /models` — list available models and their roles.
- `POST /predict` — predict a single record after validating the exact feature schema.
- `POST /analyze-csv` — accept a CSV upload, validate it, run batch inference, and return an analysis summary plus row-level results or a result identifier.
- `GET /analyses` — list recent analysis sessions.
- `GET /analyses/{analysis_id}` — fetch a saved analysis and its summary.
- `GET /metrics` — expose verified training/evaluation metrics for the dashboard.

Use Pydantic schemas for request/response validation. Configure CORS only for the frontend origin during local development. Add upload-size and row-count limits, sensible error handling, and safe CSV parsing.

Do not accept arbitrary feature vectors without schema validation. The API must apply the same preprocessing and feature ordering used during training. Treat all uploaded traffic records as untrusted input.

### Phase 3: Add persistence

Use PostgreSQL for a more complete application, or SQLite for a quick local demo.

Store only what is needed:
- analysis ID and timestamp;
- filename (or a sanitized display name);
- total rows processed;
- benign and attack counts;
- attack-category counts;
- model version/name;
- summary metrics;
- optionally row-level predictions if useful for the demo.

Avoid retaining raw uploaded traffic unnecessarily. Provide clear error handling for invalid uploads and avoid logging sensitive row contents.

### Phase 4: Build the React dashboard

Recommended pages:

1. **Overview**
   - total records analyzed;
   - benign vs. attack counts;
   - attack rate;
   - recent analysis sessions;
   - attack-category chart.

2. **Analyze Traffic**
   - CSV upload;
   - file validation feedback;
   - analysis progress/loading state;
   - results summary;
   - downloadable prediction report.

3. **Detection Results**
   - searchable/sortable table;
   - predicted label and category;
   - row details;
   - confidence only if the estimator supports a meaningful probability output.

4. **Model Evaluation**
   - verified accuracy, precision, recall, F1-score;
   - confusion matrix;
   - comparison of Random Forest, Decision Tree, and KNN;
   - evaluation dataset and class-balance context.

5. **Analysis History**
   - previous analyses and their summaries.

Suggested design direction: a professional, minimal security-operations dashboard with a dark theme, clear typography, restrained accent colors, readable charts, and useful empty/loading/error states. Avoid presenting the application as a real-time intrusion prevention system unless live capture and response functionality are actually implemented.

### Phase 5: End-to-end testing

Test the full flow:
1. Start FastAPI and confirm `/health`.
2. Open the API's `/docs` page.
3. Submit a valid example row and confirm the expected output schema.
4. Upload a small valid CSV and compare predictions with the notebook.
5. Try a malformed CSV, missing columns, extra columns, NaN/infinite values, and an oversized file.
6. Confirm the dashboard charts match backend summary counts.
7. Restart the backend and confirm persisted analysis history remains available.
8. Document known limitations and test dataset provenance.

### Phase 6: Demo preparation

- Prepare a small, reproducible sample CSV with a mix of benign and attack-labelled examples from the test set.
- Make clear that the model analyzes flow records; it does not independently capture packets or monitor live traffic.
- Present model metrics honestly and avoid claiming perfect detection.
- Include dataset and model attribution/license information as required.
- Ensure the demo works without internet access if the judging environment may have unreliable connectivity.

---

## 5. Suggested API Response Shape

A possible response shape (adapt it to the actual model and data schema; this is an example contract, not a claim about current model outputs):

```json
{
  "analysis_id": "generated-id",
  "status": "completed",
  "total_records": 1000,
  "benign_count": 850,
  "attack_count": 150,
  "attack_rate_percent": 15.0,
  "attack_categories": {
    "example_category": 90,
    "another_category": 60
  },
  "model_name": "random_forest",
  "results": []
}
```

Use actual class names from the trained model. Do not hardcode the example category names or counts.

---

## 6. Important ML and Security Considerations

- A model trained on CICIDS2017 is a dataset-based classifier, not proof that an actual live attack is occurring.
- The dataset may not represent modern or local network traffic. Describe this as a prototype and evaluate it honestly.
- Binary and multiclass models may have different feature requirements; confirm compatibility before chaining them.
- If using `predict_proba`, report it as a model score/probability estimate, not a guaranteed probability that an attack is real.
- Never load `.joblib` or pickle files from untrusted sources. Loading them can execute code.
- Never refit a scaler or reorder features during inference. Reuse the fitted preprocessing artifacts and exact training feature order.
- Keep training/evaluation data separate from production demo inputs to avoid accidental leakage.
- CSV file uploads should have size/row limits and be parsed defensively.

---

## 7. Instructions for the AI Coding Assistant

Build NetSentinel as a new application; do not copy the referenced GitHub repository's application code.

Work incrementally:
1. First inspect the available model files, selected feature JSON, preprocessing artifacts, and training notebook outputs.
2. Write a concise `MODEL_CONTRACT.md` documenting exact feature columns/order, preprocessing, target labels, model paths, and inference behavior.
3. Implement and test the model-loading/inference service in isolation.
4. Implement FastAPI endpoints and tests.
5. Implement CSV analysis and persistence.
6. Build the React dashboard and connect it to the API.
7. Add setup instructions and a repeatable demo workflow.

Ask for the actual model artifacts or relevant notebook cells when necessary. Do not fabricate model paths, features, classes, evaluation results, or successful training status. If any required artifact is missing, explain what is missing and provide the shortest route to generate or recover it.

The priority is a reliable, polished CSV-analysis demo with honest claims—not an unverified live network security system.
