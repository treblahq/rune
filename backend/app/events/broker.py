from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import suppress


class EventBroker:
    def __init__(self, *, heartbeat_seconds: float = 2.0) -> None:
        self._subscribers: set[asyncio.Queue[str]] = set()
        self._heartbeat_seconds = heartbeat_seconds

    async def publish(self, event: str = "queue.changed") -> None:
        for queue in tuple(self._subscribers):
            if queue.full():
                with suppress(asyncio.QueueEmpty):
                    queue.get_nowait()
            queue.put_nowait(event)

    async def subscribe(self) -> AsyncIterator[str]:
        queue: asyncio.Queue[str] = asyncio.Queue(maxsize=8)
        self._subscribers.add(queue)
        try:
            while True:
                try:
                    yield await asyncio.wait_for(queue.get(), timeout=self._heartbeat_seconds)
                except TimeoutError:
                    yield "heartbeat"
        finally:
            self._subscribers.discard(queue)
