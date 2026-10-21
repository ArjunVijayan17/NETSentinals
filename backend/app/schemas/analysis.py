"""Request/response schemas for CSV batch analysis."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class RowResult(BaseModel):
    row: int
    label: str
    confidence: float
    category: Optional[str] = None
    category_confidence: Optional[float] = None


class AnalysisSummary(BaseModel):
    id: str
    filename: str
    created_at: datetime
    total_rows: int
    benign_count: int
    attack_count: int
    attack_rate: float
    categories: Dict[str, int]
    model_name: str


class AnalysisDetail(AnalysisSummary):
    row_results: List[RowResult]


class AnalysisListItem(BaseModel):
    id: str
    filename: str
    created_at: datetime
    total_rows: int
    benign_count: int
    attack_count: int
    attack_rate: float
    categories: Dict[str, int]
