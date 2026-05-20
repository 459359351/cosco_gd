import ReconnectingWebSocket from "reconnecting-websocket";
import { onMounted, onUnmounted } from "vue";

import { useRealtimeStore } from "@/store/realtime";
import { useYardStore } from "@/store/yard";
import { resolveWebSocketBase } from "@/utils/wsUrl";

export function useWS() {
  const wsBase = resolveWebSocketBase();
  const realtime = useRealtimeStore();
  const yardStore = useYardStore();
  let ws: ReconnectingWebSocket | null = null;

  onMounted(() => {
    ws = new ReconnectingWebSocket(wsBase, [], {
      maxReconnectionDelay: 10000,
      minReconnectionDelay: 1000,
    });
    ws.addEventListener("open", () => {
      realtime.connected = true;
      ws?.send(JSON.stringify({ type: "subscribe", channel: "all" }));
      ws?.send(JSON.stringify({ type: "ping" }));
    });
    ws.addEventListener("close", () => {
      realtime.connected = false;
    });
    ws.addEventListener("message", (event) => {
      const data = JSON.parse(event.data);
      realtime.applyEvent(data);
      if (data.type === "alert") {
        yardStore.alerts = [
          {
            id: Date.now(),
            yard_id: data.yard_id,
            level: "high",
            alert_type: "实时",
            message: data.message,
            created_at: data.created_at,
          },
          ...yardStore.alerts,
        ].slice(0, 20);
      }
    });
  });

  onUnmounted(() => ws?.close());
}
