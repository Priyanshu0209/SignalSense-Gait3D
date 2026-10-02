import { useState, useEffect } from 'react';

import { ConnectedDevice } from './useNetworkData';

export interface GroundTruth {
  mac_address: string;
  distance: number;
  direction: number;
  orientation: string;
  los: string;
  environment: string;
  include_in_collection: boolean;
  rssi_0: number;
  n_value: number;
}

export interface DatasetConfig {
  session_name: string;
  environment: string;
  collector_device: string;
  samples_per_device: number;
  sampling_interval: number;
  stabilization_time: number;
  readings_per_sample: number;
}

export interface DatasetState {
  status: 'Stopped' | 'Running' | 'Paused';
  session_id: string | null;
  total_samples: number;
  duration: number;
  samples_per_mac: Record<string, number>;
  quality: {
    avg_rssi: number;
    missing_samples: number;
    completeness: number;
    quality_score: number;
  };
  coverage_matrix: Record<string, number>;
}

export interface DatasetSample {
  Timestamp: string;
  'Session ID': string;
  'Device Name': string;
  'MAC Address': string;
  'Ground Truth Distance': number;
  'Ground Truth Direction': number;
  Orientation: string;
  LOS: string;
  Environment: string;
  RSSI: number;
  'Signal Quality': number;
  'Collector Device': string;
  RSSI0: number;
  n_value: number;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REST_URL = `${API_URL}/api/v1/dataset`;

export function useDatasetCollection(devices: ConnectedDevice[]) {
  const [config, setConfig] = useState<DatasetConfig>({
    session_name: 'Office_Room_A',
    environment: 'Indoor - Office',
    collector_device: 'My Laptop',
    samples_per_device: 180,
    sampling_interval: 1.0,
    stabilization_time: 3.0,
    readings_per_sample: 1,
  });

  const [groundTruths, setGroundTruths] = useState<Record<string, GroundTruth>>({});
  const [state, setState] = useState<DatasetState>({
    status: 'Stopped',
    session_id: null,
    total_samples: 0,
    duration: 0,
    samples_per_mac: {},
    quality: { avg_rssi: 0, missing_samples: 0, completeness: 0, quality_score: 0 },
    coverage_matrix: {}
  });
  
  const [liveSamples, setLiveSamples] = useState<DatasetSample[]>([]);

  // Initialize Ground Truth for new devices
  useEffect(() => {
    setGroundTruths(prev => {
      const updated = { ...prev };
      let changed = false;
      devices.forEach((device, index) => {
        if (!updated[device.mac_address]) {
          // If direction is unknown, space them out evenly in a circle so they don't visually overlap on the map
          const defaultDirection = Math.round((index * (360 / Math.max(1, devices.length))) % 360);
          
          updated[device.mac_address] = {
            mac_address: device.mac_address,
            distance: device.distance?.value !== undefined && device.distance?.value !== null ? device.distance.value : 1.0, 
            direction: device.direction?.value !== undefined && device.direction?.value !== null ? device.direction.value : defaultDirection,
            orientation: 'Front',
            los: 'Yes',
            environment: 'Indoor',
            include_in_collection: true,
            rssi_0: -45.0,
            n_value: 2.5
          };
          changed = true;
          // Optionally push to backend right away
          updateGroundTruth(updated[device.mac_address]);
        }
      });
      return changed ? updated : prev;
    });
  }, [devices]);

  useEffect(() => {
    fetchState();
    fetchGroundTruths();

    let ws: WebSocket;
    let reconnectTimer: any;
    const connect = () => {
      const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      ws = new WebSocket(WS_URL);

      ws.onmessage = (event) => {
        if (event.data === "pong") return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === 'dataset_state_updated') {
            setState(payload.data);
          } else if (payload.event === 'dataset_live_samples') {
            setLiveSamples(payload.data);
          } else if (payload.event === 'dataset_gt_updated') {
            setGroundTruths(prev => ({
              ...prev,
              [payload.data.mac]: payload.data.gt
            }));
          }
        } catch (e) {
          console.error("WS Parse Error", e);
        }
      };

      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  const fetchState = async () => {
    try {
      const res = await fetch(`${REST_URL}/state`);
      if (res.ok) setState(await res.json());
    } catch (e) {
      console.error('Failed to fetch dataset state', e);
    }
  };

  const fetchGroundTruths = async () => {
    try {
      const res = await fetch(`${REST_URL}/ground_truth`);
      if (res.ok) {
        const list: GroundTruth[] = await res.json();
        const map: Record<string, GroundTruth> = {};
        list.forEach(gt => map[gt.mac_address] = gt);
        setGroundTruths(prev => ({ ...prev, ...map }));
      }
    } catch (e) {
      console.error('Failed to fetch ground truths', e);
    }
  };

  const updateConfig = async (newConfig: Partial<DatasetConfig>) => {
    const updated = { ...config, ...newConfig };
    setConfig(updated);
    try {
      await fetch(`${REST_URL}/config`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updated)
      });
    } catch (e) {
      console.error('Failed to update config', e);
    }
  };

  const updateGroundTruth = async (gt: GroundTruth) => {
    setGroundTruths(prev => ({ ...prev, [gt.mac_address]: gt }));
    try {
      await fetch(`${REST_URL}/device/${gt.mac_address}/ground_truth`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(gt)
      });
    } catch (e) {
      console.error('Failed to update ground truth', e);
    }
  };

  const startCollection = async () => {
    await fetch(`${REST_URL}/start`, { method: 'POST' });
    setLiveSamples([]);
  };

  const pauseCollection = async () => {
    await fetch(`${REST_URL}/pause`, { method: 'POST' });
  };

  const resumeCollection = async () => {
    await fetch(`${REST_URL}/resume`, { method: 'POST' });
  };

  const stopCollection = async () => {
    await fetch(`${REST_URL}/stop`, { method: 'POST' });
  };

  return {
    config,
    updateConfig,
    groundTruths,
    updateGroundTruth,
    state,
    liveSamples,
    startCollection,
    pauseCollection,
    resumeCollection,
    stopCollection
  };
}
