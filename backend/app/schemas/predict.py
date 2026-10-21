"""Request/response schemas for single-row prediction."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    """A single flow record. All 20 features are required, in any order."""

    features: dict[str, float] = Field(
        ..., description="Map of the 20 feature names to numeric values."
    )


class PredictResponse(BaseModel):
    label: str = Field(..., description="'Benign' or 'Attack'")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    category: Optional[str] = Field(
        None, description="Attack category, present only for Attack rows"
    )
    category_confidence: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Category confidence score"
    )
    model_name: str = Field(..., description="Binary model used")
