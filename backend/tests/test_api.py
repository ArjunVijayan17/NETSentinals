"""API endpoint tests (Phase 5)."""
import io
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.config import REQUIRED_FEATURES
from backend.app.main import app

SAMPLE_CSV = Path(__file__).resolve().parents[2] / "sample-data" / "sample.csv"


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def _feature_payload():
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
    return values


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ok"
    assert all(body["models"].values())


def test_models(client):
    resp = client.get("/models")
    assert resp.status_code == 200
    names = [m["name"] for m in resp.json()]
    assert set(names) == {"random_forest", "decision_tree", "knn", "attack_type"}


def test_metrics(client):
    resp = client.get("/metrics")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body["binary"]) == {"random_forest", "decision_tree", "knn"}
    assert body["attack_type"]["summary"]["accuracy"] == 0.9994


def test_predict_happy_path(client):
    resp = client.post("/predict", json={"features": _feature_payload()})
    assert resp.status_code == 200
    body = resp.json()
    assert body["label"] in ("Benign", "Attack")
    assert 0.0 <= body["confidence"] <= 1.0


def test_predict_missing_feature(client):
    payload = _feature_payload()
    payload.pop("Destination Port")
    resp = client.post("/predict", json={"features": payload})
    assert resp.status_code == 422


def test_analyze_csv_happy_path(client):
    with open(SAMPLE_CSV, "rb") as fh:
        resp = client.post(
            "/analyze-csv",
            files={"file": ("sample.csv", fh, "text/csv")},
        )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_rows"] > 0
    assert body["benign_count"] + body["attack_count"] == body["total_rows"]
    assert "id" in body


def test_analyze_csv_missing_columns(client):
    csv_bytes = b"Destination Port\n80\n443\n"
    resp = client.post(
        "/analyze-csv",
        files={"file": ("bad.csv", csv_bytes, "text/csv")},
    )
    assert resp.status_code == 422
    assert "Missing required columns" in resp.json()["detail"]


def test_analyze_csv_nan_values(client):
    header = ",".join(REQUIRED_FEATURES)
    nan_row = ",".join([""] * 20)
    csv_bytes = (header + "\n" + nan_row + "\n").encode()
    resp = client.post(
        "/analyze-csv",
        files={"file": ("nan.csv", csv_bytes, "text/csv")},
    )
    assert resp.status_code == 422
    assert "NaN or infinite" in resp.json()["detail"]


def test_analyses_list_and_detail(client):
    listing = client.get("/analyses").json()
    assert isinstance(listing, list)
    if listing:
        aid = listing[0]["id"]
        detail = client.get(f"/analyses/{aid}")
        assert detail.status_code == 200
        assert detail.json()["id"] == aid
        dl = client.get(f"/analyses/{aid}/download")
        assert dl.status_code == 200
        assert dl.headers["content-type"].startswith("text/csv")


def test_analysis_not_found(client):
    resp = client.get("/analyses/does-not-exist")
    assert resp.status_code == 404
