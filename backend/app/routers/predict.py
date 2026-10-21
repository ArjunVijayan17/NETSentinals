"""Single-row prediction endpoint."""
from __future__ import annotations

import pandas as pd
from fastapi import APIRouter, HTTPException

from ..config import REQUIRED_FEATURES
from ..models.inference import predict_attack_type, predict_binary
from ..schemas.predict import PredictRequest, PredictResponse

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    try:
        df = pd.DataFrame([payload.features])[REQUIRED_FEATURES]
    except KeyError as exc:
        raise HTTPException(status_code=422, detail=f"Missing feature: {exc}") from exc

    try:
        binary = predict_binary("random_forest", df)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    category = None
    category_confidence = None
    if binary["label"] == "Attack":
        try:
            attack = predict_attack_type(df)
            category = attack["category"]
            category_confidence = attack["confidence"]
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    return PredictResponse(
        label=binary["label"],
        confidence=binary["confidence"],
        category=category,
        category_confidence=category_confidence,
        model_name="random_forest",
    )
