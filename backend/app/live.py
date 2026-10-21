"""Live flow streaming hub.

Streams flow records through the inference pipeline in real time. Ambient
traffic is replayed from real benign CICIDS rows; the ``/live/simulate``
endpoint injects real attack rows so a clean network can still demo attacks.
"""
from __future__ import annotations

import asyncio
import json
import random
from datetime import datetime, timezone

import pandas as pd

from .config import PROJECT_ROOT, REQUIRED_FEATURES
from .models.inference import predict_attack_type, predict_binary

INTERVAL_SECONDS = 1.0

_benign_pool: list[dict] = []
_attack_pool: list[dict] = []
_subscribers: set[asyncio.Queue] = set()
_pending_attacks = 0
_task: asyncio.Task | None = None


def init_live() -> None:
    """Preload benign/attack flow pools from the sample CSV.

    The attack pool is filtered to rows the model actually detects, so the
    "simulate" action reliably produces visible attacks (some CICIDS attack
    rows are genuinely hard for the RF and would otherwise show as benign).
    """
    global _benign_pool, _attack_pool

    csv_path = PROJECT_ROOT / "sample-data" / "sample.csv"
    if not csv_path.exists():
        return

    df = pd.read_csv(csv_path)
    df.columns = [str(c).strip() for c in df.columns]

    if "ground_truth_label" not in df.columns:
        return

    x = df[REQUIRED_FEATURES]
    mask = df["ground_truth_label"] == "BENIGN"
    _benign_pool = x[mask].to_dict("records")

    for row in x[~mask].to_dict("records"):
        try:
            if predict_binary("random_forest", pd.DataFrame([row])[REQUIRED_FEATURES])[
                "label"
            ] == "Attack":
                _attack_pool.append(row)
        except Exception:
            continue


def start_live() -> None:
    global _task
    if _task is None or _task.done():
        _task = asyncio.create_task(_loop())


def stop_live() -> None:
    global _task
    if _task is not None and not _task.done():
        _task.cancel()


def inject_attacks(n: int) -> None:
    global _pending_attacks
    _pending_attacks += max(0, n)


def _predict(row: dict, source: str) -> dict:
    df = pd.DataFrame([row])[REQUIRED_FEATURES]
    binary = predict_binary("random_forest", df)

    category = None
    category_confidence = None
    if binary["label"] == "Attack":
        attack = predict_attack_type(df)
        category = attack["category"]
        category_confidence = attack["confidence"]

    return {
        "type": "flow",
        "source": source,
        "label": binary["label"],
        "confidence": round(binary["confidence"], 4),
        "category": category,
        "category_confidence": (
            round(category_confidence, 4) if category_confidence is not None else None
        ),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def _publish(event: dict) -> None:
    payload = json.dumps(event)
    for queue in list(_subscribers):
        try:
            queue.put_nowait(payload)
        except asyncio.QueueFull:
            pass


async def _loop() -> None:
    global _pending_attacks
    while True:
        if _subscribers and (_benign_pool or _attack_pool):
            if _pending_attacks > 0 and _attack_pool:
                _pending_attacks -= 1
                row = random.choice(_attack_pool)
                source = "simulated"
            elif _benign_pool:
                row = random.choice(_benign_pool)
                source = "ambient"
            else:
                row = random.choice(_attack_pool)
                source = "ambient"

            _publish(_predict(row, source))

        await asyncio.sleep(INTERVAL_SECONDS)


def subscribe() -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue(maxsize=1000)
    _subscribers.add(queue)
    return queue


def unsubscribe(queue: asyncio.Queue) -> None:
    _subscribers.discard(queue)
