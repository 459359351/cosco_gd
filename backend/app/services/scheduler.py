from datetime import datetime
import random

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.services.mock_data import mock_alerts
from app.ws.pubsub import publish

scheduler = AsyncIOScheduler()


async def _emit_realtime_tick() -> None:
    sample_alert = random.choice(mock_alerts())
    payload = {
        "type": "alert",
        "yard_id": sample_alert["yard_id"],
        "message": sample_alert["message"],
        "created_at": datetime.utcnow().isoformat(),
    }
    await publish("cockpit.realtime", payload)


def start_scheduler() -> None:
    if scheduler.running:
        return
    scheduler.add_job(_emit_realtime_tick, "interval", seconds=20, id="realtime-tick")
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)
