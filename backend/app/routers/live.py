"""Live-streaming endpoints: SSE flow stream + attack injection."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Query, Request
from fastapi.responses import StreamingResponse

from .. import live

router = APIRouter()


@router.get("/live/stream")
async def stream(request: Request):
    queue = live.subscribe()

    async def gen():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    payload = await asyncio.wait_for(queue.get(), timeout=15)
                    yield f"data: {payload}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            live.unsubscribe(queue)

    return StreamingResponse(gen(), media_type="text/event-stream")


@router.post("/live/simulate")
def simulate(count: int = Query(20, ge=1, le=500)):
    live.inject_attacks(count)
    return {"injected": count}
