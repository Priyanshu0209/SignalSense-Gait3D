import { useState, useEffect } from 'react';


const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REST_URL = `${API_URL}/api/v1/localization`;

export interface ReplayFrame {
  mac_address: string;
  gt_distance: number;
  gt_direction: number;
  rssi: number;
  est_distance: number;
  est_direction: number;
  abs_error: number;
  confidence: number;
  index: number;
  total: number;
  speed: number;
  is_playing: boolean;
}

export interface ReplayState {
  dataset: string;
  is_playing: boolean;
  speed: number;
  current_index: number;
  total_samples: number;
}

export function useLocalization() {
  const [replayFrame, setReplayFrame] = useState<ReplayFrame | null>(null);
  const [replayState, setReplayState] = useState<ReplayState | null>(null);

  useEffect(() => {
    let ws: WebSocket;
    let reconnectTimer: any;
    
    const connect = () => {
      const WS_URL_NATIVE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      ws = new WebSocket(WS_URL_NATIVE);
      
      ws.onmessage = (event) => {
        if (event.data === "pong") return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === 'localization_replay_frame') {
            setReplayFrame(payload.data);
          } else if (payload.event === 'localization_replay_state') {
            setReplayState(payload.data);
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

  const loadReplay = async (dataset: string) => {
    await fetch(`${REST_URL}/replay/load`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset })
    });
  };

  const playReplay = async () => fetch(`${REST_URL}/replay/play`, { method: 'POST' });
  const pauseReplay = async () => fetch(`${REST_URL}/replay/pause`, { method: 'POST' });
  const seekReplay = async (index: number) => fetch(`${REST_URL}/replay/seek/${index}`, { method: 'POST' });
  const setSpeed = async (speed: number) => fetch(`${REST_URL}/replay/speed/${speed}`, { method: 'POST' });

  const runBenchmark = async (dataset: string, modelIds: string[]) => {
    const res = await fetch(`${REST_URL}/benchmark/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dataset, model_ids: modelIds })
    });
    return res.json();
  };

  const generateReport = async (benchmarkData: any) => {
    const res = await fetch(`${REST_URL}/report/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(benchmarkData)
    });
    return res.json();
  };

  return {
    replayFrame,
    replayState,
    loadReplay,
    playReplay,
    pauseReplay,
    seekReplay,
    setSpeed,
    runBenchmark,
    generateReport
  };
}
