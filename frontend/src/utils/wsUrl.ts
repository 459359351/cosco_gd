/**
 * 开发环境常见错误：VITE_WS_BASE=ws://localhost/ws/realtime（缺端口）会连到 80，
 * 应改为与当前页面同 host（如 localhost:5174）以走 Vite 代理。
 */
export function resolveWebSocketBase(): string {
  const raw = (import.meta.env.VITE_WS_BASE as string | undefined)?.trim();
  if (!raw) {
    return `${window.location.origin.replace("http", "ws")}/ws/realtime`;
  }
  try {
    const normalized = raw.replace(/^ws:/i, "http:").replace(/^wss:/i, "https:");
    const u = new URL(normalized);
    const local = u.hostname === "localhost" || u.hostname === "127.0.0.1";
    if (local && !u.port) {
      const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
      return `${proto}//${window.location.host}${u.pathname}${u.search}`;
    }
  } catch {
    /* 非标准 URL 时原样使用 */
  }
  return raw;
}
