"""CSV batch analysis and persistence endpoints."""
from __future__ import annotations

import asyncio
import csv
import io
import uuid
from collections import Counter

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from fastapi.responses import StreamingResponse

from ..config import MAX_UPLOAD_BYTES, MAX_UPLOAD_ROWS
from ..db import crud
from ..models.inference import batch_predict
from ..schemas.analysis import AnalysisDetail, AnalysisListItem

router = APIRouter()


@router.post("/analyze-csv", response_model=AnalysisDetail)
async def analyze_csv(
    file: UploadFile = File(...),
    model_name: str = Query("random_forest"),
):
    raw = await file.read()
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=422,
            detail=f"File exceeds the 50 MB limit ({len(raw)} bytes).",
        )
    if len(raw) == 0:
        raise HTTPException(status_code=422, detail="Uploaded file is empty.")

    if model_name not in ("random_forest", "decision_tree", "knn"):
        raise HTTPException(status_code=422, detail=f"Unknown model: {model_name}")

    # Heavy pandas work runs off the event loop.
    results, counts = await asyncio.to_thread(_run_analysis, raw, model_name)

    analysis_id = str(uuid.uuid4())
    filename = file.filename or "upload.csv"

    categories = dict(Counter(r["category"] for r in results if r["category"]))
    benign_count = counts["benign"]
    attack_count = counts["attack"]
    total = benign_count + attack_count
    attack_rate = round((attack_count / total * 100), 4) if total else 0.0

    record = crud.save_analysis(
        analysis_id=analysis_id,
        filename=filename,
        total_rows=total,
        benign_count=benign_count,
        attack_count=attack_count,
        attack_rate=attack_rate,
        categories=categories,
        model_name=model_name,
        row_results=results,
    )

    return _detail(
        analysis_id, filename, record.created_at, total, benign_count,
        attack_count, attack_rate, categories, model_name, results,
    )


def _run_analysis(raw: bytes, model_name: str):
    """Parse CSV and run the chained pipeline. Returns (results, counts)."""
    import pandas as pd

    try:
        df = pd.read_csv(io.BytesIO(raw))
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"Could not parse CSV: {exc}") from exc

    df.columns = [str(c).strip() for c in df.columns]

    if len(df) > MAX_UPLOAD_ROWS:
        raise HTTPException(
            status_code=422,
            detail=f"File has {len(df)} rows; the limit is {MAX_UPLOAD_ROWS}.",
        )

    try:
        results = batch_predict(df, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    counts = {
        "benign": sum(1 for r in results if r["label"] == "Benign"),
        "attack": sum(1 for r in results if r["label"] == "Attack"),
    }
    return results, counts


def _detail(
    analysis_id, filename, created_at, total, benign, attack, attack_rate,
    categories, model_name, row_results,
):
    return AnalysisDetail(
        id=analysis_id,
        filename=filename,
        created_at=created_at,
        total_rows=total,
        benign_count=benign,
        attack_count=attack,
        attack_rate=attack_rate,
        categories=categories,
        model_name=model_name,
        row_results=row_results,
    )


@router.get("/analyses", response_model=list[AnalysisListItem])
def list_analyses(limit: int = Query(100, ge=1, le=1000)):
    records = crud.list_analyses(limit=limit)
    return [
        AnalysisListItem(
            id=r.id,
            filename=r.filename,
            created_at=r.created_at,
            total_rows=r.total_rows,
            benign_count=r.benign_count,
            attack_count=r.attack_count,
            attack_rate=r.attack_rate,
            categories=r.categories_dict(),
        )
        for r in records
    ]


@router.get("/analyses/{analysis_id}", response_model=AnalysisDetail)
def get_analysis(analysis_id: str):
    record = crud.get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")
    return _detail(
        record.id,
        record.filename,
        record.created_at,
        record.total_rows,
        record.benign_count,
        record.attack_count,
        record.attack_rate,
        record.categories_dict(),
        record.model_name,
        record.row_results_list(),
    )


@router.get("/analyses/{analysis_id}/download")
def download_analysis(analysis_id: str):
    record = crud.get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    rows = record.row_results_list()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["row", "label", "confidence", "category", "category_confidence"])
    for r in rows:
        writer.writerow(
            [r["row"], r["label"], r["confidence"], r.get("category", ""), r.get("category_confidence", "")]
        )

    safe_name = record.filename.replace('"', "_")
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="prediction_{safe_name}"'},
    )
