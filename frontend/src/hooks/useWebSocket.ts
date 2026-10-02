// @ts-nocheck
import { useEffect, useRef, useState } from 'react';
import { io, Socket } from 'socket.io-client';
import { DeviceState } from '../types';

// Using native WebSocket since backend is FastAPI standard websockets, 
// wait, we installed socket.io-client earlier but backend uses native FastAPI websockets. 
// We should use native browser WebSocket for FastAPI.

export function useSignalSenseWebSocket(url: string) {
  const [devices, setDevices] = useState<Record<string, DeviceState>>({});
  const [isConnected, setIsConnected] = useState(false);
  const ws = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Initial fetch to populate state before WS events come in
    fetch('http://localhost:8000/api/v1/devices')
      .then(res => res.json())
      .then((res: any) => {
        const data = res.data || res;
        const initialMap: Record<string, DeviceState> = {};
        data.forEach((d: any) => {
          initialMap[d.mac_address] = {
            mac: d.mac_address,
            hostname: d.hostname,
            ip: d.ip_address,
            manufacturer: d.manufacturer,
            rssi: d.current_rssi,
            signal: d.signal_classification,
            distance: d.distance_classification,
            trend: d.signal_trend,
            animation: d.animation_state,
            status: d.online_status ? "online" : "offline",
            connection_duration: d.connection_duration,
            timestamp: d.last_seen
          };
        });
        setDevices(initialMap);
      })
      .catch(console.error);

    const connect = () => {
      ws.current = new WebSocket(url);
      
      ws.current.onopen = () => {
        setIsConnected(true);
        // Heartbeat
        setInterval(() => {
          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send("ping");
          }
        }, 30000);
      };

      ws.current.onclose = () => {
        setIsConnected(false);
        // Reconnect after 3 seconds
        setTimeout(connect, 3000);
      };

      ws.current.onmessage = (event) => {
        if (event.data === "pong") return;
        
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === "device_updated" && Array.isArray(payload.data)) {
            setDevices(prev => {
              const next = { ...prev };
              payload.data.forEach((update: DeviceState) => {
                next[update.mac] = { ...next[update.mac], ...update };
              });
              return next;
            });
          }
        } catch (e) {
          console.error("WS Parse Error", e);
        }
      };
    };

    connect();

    return () => {
      ws.current?.close();
    };
  }, [url]);

  return { devices: Object.values(devices), isConnected };
}
