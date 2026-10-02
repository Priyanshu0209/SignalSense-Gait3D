import { useState, useEffect, useCallback } from 'react';


export type MetricStatus = 'REAL' | 'ESTIMATED' | 'UNKNOWN';

export interface MetricValue<T> {
  value: T | null;
  status: MetricStatus;
  confidence: number;
  source: string;
}

export interface ConnectedDevice {
  mac_address: string;
  ip_address: string;
  hostname?: string;
  
  current_rssi: MetricValue<number>;
  previous_rssi?: number | null;
  moving_average_rssi?: number | null;
  signal_quality?: number | null;
  
  signal_classification?: string;
  distance_classification?: string;
  signal_trend?: string;
  stability_score?: number | null;
  health_score?: string;
  behavior_profile?: string;
  ai_explanation?: any;
  twin_mode?: string;
  
  distance: MetricValue<number>;
  direction: MetricValue<number>;
  movement: MetricValue<string>;
  activity_score?: number;
  
  animation_state?: {
    color: string;
    pulse_speed: string;
    glow_intensity: string;
  };
  online_status?: boolean;
  connection_duration?: number;
  device_type?: string;
  manufacturer?: string;
  last_seen: string;
  tx_rate?: number;
  rx_rate?: number;
}

export interface RouterCapabilities {
  supports_rssi: boolean;
  supports_clients: boolean;
  supports_cpu: boolean;
  supports_memory: boolean;
  supports_channels: boolean;
  supports_tx_rate: boolean;
  supports_rx_rate: boolean;
  supports_hostname: boolean;
  supports_vendor: boolean;
  supports_firmware: boolean;
}

export interface RouterStatus {
  router_name: string;
  router_model: string;
  vendor: string;
  firmware_version: string;
  gateway_ip: string;
  mac_address: string;
  connection_type: string;
  cpu_usage: number | null;
  memory_usage: number | null;
  network_status: string;
  internet_status: string;
  uptime_seconds: number;
  connected_devices_count: number;
  timestamp: string;
  wan_ip?: string;
  lan_ip?: string;
  wifi_channel?: number;
  frequency?: string;
  bandwidth_mbps?: number;
  packet_loss_percent?: number;
  latency_ms?: number;
  jitter_ms?: number;
  dns_status?: string;
  signal_quality?: number;
  adapter_type?: string;
  connection_status?: string;
  capabilities: RouterCapabilities;
}

export interface NetworkEvent {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
}

export function useNetworkData() {
  const [devices, setDevices] = useState<ConnectedDevice[]>([]);
  const [routerStatus, setRouterStatus] = useState<RouterStatus | null>(null);
  const [events, setEvents] = useState<NetworkEvent[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  const addEvent = useCallback((type: 'info' | 'warning' | 'error' | 'success', message: string) => {
    setEvents(prev => {
      const newEvent = { id: Math.random().toString(36).substring(7), type, message, timestamp: new Date().toISOString() };
      return [newEvent, ...prev].slice(0, 50); // Keep last 50 events
    });
  }, []);

  const processDevices = useCallback((data: ConnectedDevice[]) => {
    // Bug 1 fix: Exclude gateway/router from client list entirely.
    // The gateway is shown as the root hub in Topology — NOT as a connected client.
    // Including it inflated the device count compared to what Gait3D generates avatars for.
    const clients = data.filter(d =>
      d.hostname !== 'Gateway' &&
      d.device_type !== 'Router' &&
      !(d.hostname || '').toLowerCase().includes('gateway')
    );
    return clients;
  }, []);

  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimer: any;
    
    const connect = () => {
      const wsUrl = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        addEvent('success', 'Connected to backend server');
        // Heartbeat
        setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send("ping");
          }
        }, 30000);
      };

      ws.onclose = () => {
        setIsConnected(false);
        addEvent('error', 'Disconnected from backend server');
        reconnectTimer = setTimeout(connect, 3000);
      };

      ws.onmessage = (event) => {
        if (event.data === "pong") return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === 'device_updated' && Array.isArray(payload.data)) {
            requestAnimationFrame(() => {
              setDevices(prev => {
                const next = [...prev];
                payload.data.forEach((update: ConnectedDevice) => {
                  const idx = next.findIndex(d => d.mac_address === update.mac_address);
                  if (idx >= 0) {
                    next[idx] = { ...next[idx], ...update };
                  } else {
                    next.push(update);
                  }
                });
                return processDevices(next);
              });
            });
          } else if (payload.event === 'router_updated') {
            setRouterStatus(payload.data);
          }
        } catch (e) {
          console.error("WS Parse Error", e);
        }
      };
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, [addEvent, processDevices]);


  // Polling fallback since WS backend might not be emitting these specific events yet
  useEffect(() => {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
    
    const fetchData = async () => {
      try {
        const [devicesRes, statusRes] = await Promise.all([
          fetch(`${API_URL}/devices`),
          fetch(`${API_URL}/router/status`)
        ]);
        
        if (devicesRes.ok) {
          const devs = await devicesRes.json();
          setDevices(processDevices(devs.data || devs));
        }
        
        if (statusRes.ok) {
          const status = await statusRes.json();
          setRouterStatus(status.data || status);
        }
      } catch (e) {
        console.error("Failed to fetch network data", e);
      }
    };

    fetchData(); // Initial fetch
    const interval = setInterval(fetchData, 1000); // 1-second auto refresh
    
    return () => clearInterval(interval);
  }, [processDevices]);

  const onlineDevices = devices.filter(d => d.online_status !== false);

  return { devices, onlineDevices, routerStatus, events, isConnected, addEvent };
}
