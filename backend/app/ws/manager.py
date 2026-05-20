from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()
        self.subscriptions: defaultdict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)
        for listeners in self.subscriptions.values():
            listeners.discard(websocket)

    async def subscribe(self, websocket: WebSocket, channel: str) -> None:
        self.subscriptions[channel].add(websocket)
        await websocket.send_json({"type": "subscribed", "channel": channel})

    async def broadcast(self, payload: dict, channel: str | None = None) -> None:
        targets = self.connections if channel is None else self.subscriptions[channel]
        for conn in list(targets):
            await conn.send_json(payload)


manager = ConnectionManager()
