import asyncio

import pytest

from app.events.broker import EventBroker


@pytest.mark.asyncio
async def test_idle_subscriber_receives_heartbeat() -> None:
    broker = EventBroker(heartbeat_seconds=0.01)
    subscription = broker.subscribe()

    event = await asyncio.wait_for(anext(subscription), timeout=0.1)

    assert event == "heartbeat"
    await subscription.aclose()
