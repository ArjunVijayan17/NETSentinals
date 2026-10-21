"""CRUD helpers for analysis persistence."""
from __future__ import annotations

import json
from typing import Dict, List, Optional

from sqlalchemy import desc

from .database import AnalysisRecord, SessionLocal


def save_analysis(
    analysis_id: str,
    filename: str,
    total_rows: int,
    benign_count: int,
    attack_count: int,
    attack_rate: float,
    categories: Dict[str, int],
    model_name: str,
    row_results: List[dict],
) -> AnalysisRecord:
    record = AnalysisRecord(
        id=analysis_id,
        filename=filename,
        total_rows=total_rows,
        benign_count=benign_count,
        attack_count=attack_count,
        attack_rate=attack_rate,
        categories=json.dumps(categories),
        model_name=model_name,
        row_results=json.dumps(row_results),
    )
    with SessionLocal() as session:
        session.add(record)
        session.commit()
        session.refresh(record)
        return record


def get_analysis(analysis_id: str) -> Optional[AnalysisRecord]:
    with SessionLocal() as session:
        return session.get(AnalysisRecord, analysis_id)


def list_analyses(limit: int = 100) -> List[AnalysisRecord]:
    with SessionLocal() as session:
        return (
            session.query(AnalysisRecord)
            .order_by(desc(AnalysisRecord.created_at))
            .limit(limit)
            .all()
        )
