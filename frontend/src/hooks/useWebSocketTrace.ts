import { useEffect, useState, useRef } from 'react';
import { TraceEvent } from '../lib/api';

export function useWebSocketTrace(sessionId: string | null) {
  const [traceEvents, setTraceEvents] = useState<TraceEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setTraceEvents([]);
      setIsConnected(false);
      return;
    }

    const wsUrl = `ws://localhost:8000/ws/research/${sessionId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      try {
        const parsed: TraceEvent = JSON.parse(event.data);
        setTraceEvents((prev) => [...prev, parsed]);
      } catch (err) {
        console.warn("Failed to parse trace WebSocket message", err);
      }
    };

    ws.onerror = (err) => {
      console.error("WebSocket connection error", err);
      setError("WebSocket connection failed. Ensure FastAPI server is running on http://localhost:8000.");
      setIsConnected(false);
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [sessionId]);

  return { traceEvents, isConnected, error, clearTraces: () => setTraceEvents([]) };
}
