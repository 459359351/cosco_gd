import asyncio
from datetime import datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws.manager import manager
from app.ws.pubsub import publish

ws_router = APIRouter()


@ws_router.websocket("/ws/realtime")
async def realtime_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    heartbeat_task = asyncio.create_task(_heartbeat(websocket))
    try:
        while True:
            msg = await websocket.receive_json()
            event_type = msg.get("type")
            if event_type == "subscribe":
                await manager.subscribe(websocket, msg.get("channel", "all"))
            elif event_type == "ping":
                await websocket.send_json({"type": "pong", "ts": datetime.utcnow().isoformat()})
            elif event_type == "broadcast":
                payload = msg.get("payload", {})
                await publish("cockpit.realtime", {"type": "event", "payload": payload})
            else:
                await websocket.send_json({"type": "ack", "message": "received"})
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    finally:
        heartbeat_task.cancel()


async def _heartbeat(websocket: WebSocket) -> None:
    while True:
        await asyncio.sleep(30)
        await websocket.send_json({"type": "heartbeat", "ts": datetime.utcnow().isoformat()})
