import { useState, useEffect, useCallback, useRef } from 'react';

export interface GaitActivity {
  mac_address: string;
  device_name: string;
  activity: 'Still' | 'Standing' | 'Walking' | 'Running' | 'Sitting' | 'Falling' | 'Unknown';
  confidence_pct: number;
  anomaly_detected: boolean;
  features: {
    variance: number;
    range_dbm: number;
    zero_crossing_rate: number;
    dominant_freq_hz: number;
    spectral_entropy: number;
  };
  class_probabilities: Record<string, number>;
  timestamp: string;
}

export interface GaitMetric {
  mac_address: string;
  device_name: string;
  cadence_rpm: number;
  stride_period_sec: number;
  step_symmetry_pct: number;
  perturbation_depth_dbm: number;
  gait_stability_score: string;
  waveform: Array<{ time_offset: number; rssi: number }>;
  timestamp: string;
}

export interface SkeletonJoints {
  [key: string]: { x: number; y: number; z: number };
}

export interface SubjectTelemetry {
  id: string;
  device_mac: string;
  mac_address?: string;
  name: string;
  ip_address?: string;
  rssi?: number;
  color_hex: string;
  color_int: number;
  activity_state: 'Idle' | 'Walking' | 'Running' | 'Standing' | 'Disconnected' | 'Still' | string;
  position: { x: number; y: number; z: number };
  router_distance_m: number;
  estimated_distance_m?: number;
  uncertainty_radius_m?: number;
  ground_truth_distance_m?: number;
  actual_distance_m?: number;
  ground_truth_error_m?: number;
  localization_mode?: string;
  speed_mps: number;
  heading_rad: number;
  heading_deg: number;
  cadence_rpm: number;
  confidence_pct: number;
  sensor_modality?: string;
  last_seen_iso?: string;
  last_update_str?: string;
  is_connected?: boolean;
  connection_status?: string;
  // Future Multisensor Extension Points
  csi_matrix?: Array<Array<number>>;
  ble_aoa_deg?: number;
  uwb_range_m?: number;
  mmwave_doppler_mps?: number;
}

export interface Scene3DFrame {
  timestamp: string;
  room_dimensions: { width_x: number; length_y: number; height_z: number };
  access_points: Array<{ id: string; x: number; y: number; z: number; frequency: string; power_dbm: number }>;
  subjects?: Array<SubjectTelemetry>;
  human_subject: {
    activity_state: string;
    cadence_rpm: number;
    speed_mps?: number;
    position: { x: number; y: number; z: number };
    heading_angle_rad: number;
    confidence_pct?: number;
    estimation_model?: string;
    skeleton_joints?: SkeletonJoints; // Deprecated for simple RSSI; preserved for hybrid camera ground-truth calibration
  };
  rf_waves: Array<{ ap_id: string; origin: { x: number; y: number; z: number }; radius: number; intensity: number; distance_to_subject_m?: number; collision: boolean }>;
  client_nodes: Array<{ mac: string; name: string; cadence: number; stability: string }>;
  
  // Sync diagnostics from backend kinematic generator
  topology_total_count?: number;
  topology_online_count?: number;
  avatar_count?: number;
  sync_ok?: boolean;

  // FUTURE-READY MODULAR EXTENSION POINTS (Wi-Fi CSI, mmWave Radar, Multi-Subject Tracking)
  additional_subjects?: Array<{ id: string; position: { x: number; y: number; z: number }; activity_state: string; confidence_pct: number }>;
  csi_amplitude_matrix?: Array<Array<number>>; // For OFDM subcarrier attenuation mapping
  mmwave_point_cloud?: Array<{ x: number; y: number; z: number; doppler_velocity_mps: number; snr: number }>; // For 60GHz/77GHz mmWave radar
  voxel_grid_3d?: Array<{ x: number; y: number; z: number; attenuation_density: number }>;
}

export interface GaitExperimentSummary {
  id: string;
  title: string;
  subject_id: string;
  scenario: string;
  room_name?: string;
  environment?: string;
  router_model?: string;
  router_position?: { x: number; y: number; z: number };
  number_of_connected_devices?: number;
  sampling_frequency?: string;
  operator_name?: string;
  duration_sec: number;
  sample_count: number;
  dataset_filename: string;
  json_filename?: string;
  metadata_filename?: string;
  sha256_hash: string;
  metrics_summary: { avg_cadence: number; symmetry_index: number; har_accuracy_pct: number };
  ground_truth?: {
    actual_distance_m: number;
    actual_room_position?: { x: number; y: number; z: number };
    los_status?: string;
    obstacle_count?: number;
    environment_notes?: string;
  };
  ai_validation?: {
    mae_m: number;
    rmse_m: number;
    mape_pct: number;
    std_error_m: number;
    confidence_distribution?: Record<string, number>;
  };
  timestamp: string;
  status: string;
}

export function useGait3D() {
  const [activities, setActivities] = useState<GaitActivity[]>([]);
  const [metrics, setMetrics] = useState<GaitMetric[]>([]);
  const [sceneFrame, setSceneFrame] = useState<Scene3DFrame | null>(null);
  const [simulationEnabled, setSimulationEnabled] = useState<boolean>(false);
  const [experiments, setExperiments] = useState<GaitExperimentSummary[]>([]);
  const [activeTrial, setActiveTrial] = useState<any | null>(null);
  const [isRecording, setIsRecording] = useState<boolean>(false);
  const [samplesRecorded, setSamplesRecorded] = useState<number>(0);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
  const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

  const refreshState = useCallback(async () => {
    try {
      const res = await fetch(`${API_URL}/gait3d/state`);
      if (res.ok) {
        const data = await res.json();
        if (data.activities) setActivities(data.activities);
        if (data.gait_metrics) setMetrics(data.gait_metrics);
        if (data.collector_status) setSimulationEnabled(data.collector_status.simulation_enabled);
      }
      
      const frameRes = await fetch(`${API_URL}/gait3d/frame3d`);
      if (frameRes.ok) {
        const f = await frameRes.json();
        const subs = f?.subjects || [];
        console.log(`[DEBUG LOG: FRONTEND STORE (REST)] Received frame3d with exactly ${subs.length} subject(s):`, subs.map((s: any) => s.id));
        setSceneFrame(f);
      }

      const expRes = await fetch(`${API_URL}/gait3d/experiments`);
      if (expRes.ok) {
        const ed = await expRes.json();
        if (ed.experiments) setExperiments(ed.experiments);
        if (ed.active_status) {
          setIsRecording(ed.active_status.is_recording);
          setActiveTrial(ed.active_status.active_trial);
          setSamplesRecorded(ed.active_status.samples_buffered);
        }
      }
    } catch (err) {
      console.error('Failed to fetch Gait3D state:', err);
    }
  }, [API_URL]);

  useEffect(() => {
    refreshState();
    const interval = setInterval(refreshState, 1500);

    const connectWs = () => {
      wsRef.current = new WebSocket(WS_URL);
      wsRef.current.onopen = () => setIsConnected(true);
      wsRef.current.onclose = () => {
        setIsConnected(false);
        setTimeout(connectWs, 3000);
      };
      wsRef.current.onmessage = (event) => {
        if (event.data === 'pong') return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === 'gait_live_telemetry') {
            if (payload.data.activities) setActivities(payload.data.activities);
            if (payload.data.gait_metrics) setMetrics(payload.data.gait_metrics);
            if (payload.data.simulation_enabled !== undefined) setSimulationEnabled(payload.data.simulation_enabled);
          } else if (payload.event === 'gait_3d_frame') {
            const subs = payload.data?.subjects || [];
            console.log(`[DEBUG LOG: FRONTEND STORE (WEBSOCKET)] Received gait_3d_frame with exactly ${subs.length} subject(s):`, subs.map((s: any) => s.id));
            setSceneFrame(payload.data);
          } else if (payload.event === 'gait_experiment_progress') {
            setSamplesRecorded(payload.data.samples_recorded);
          }
        } catch (e) {
          // ignore parsing err
        }
      };
    };

    connectWs();
    return () => {
      clearInterval(interval);
      wsRef.current?.close();
    };
  }, [WS_URL, refreshState]);

  const toggleSimulation = async (enabled: boolean, activityOverride?: string) => {
    try {
      await fetch(`${API_URL}/gait3d/simulation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled, activity_override: activityOverride })
      });
      setSimulationEnabled(enabled);
      refreshState();
    } catch (err) {
      console.error('Toggle simulation error:', err);
    }
  };

  const startTrial = async (
    title: string,
    subject_id: string,
    scenario: string,
    speed_ms: number = 1.3,
    room_name?: string,
    environment?: string,
    router_model?: string,
    operator_name?: string,
    ground_truth?: any
  ) => {
    try {
      const res = await fetch(`${API_URL}/gait3d/experiment/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title,
          subject_id,
          scenario,
          walking_speed_ms: speed_ms,
          room_name: room_name || "RF Biomedical Motion Laboratory",
          environment: environment || "Indoor Laboratory (LOS / Soft Partitions)",
          router_model: router_model || "Netgear Nighthawk X4S / IEEE 802.11ac",
          operator_name: operator_name || "Lead RF Sensing Researcher",
          ground_truth
        })
      });
      if (res.ok) {
        await refreshState();
        return { status: 'success' };
      }
    } catch (err) {
      console.error('Start trial error:', err);
    }
    return { status: 'error' };
  };

  const stopTrial = async () => {
    try {
      const res = await fetch(`${API_URL}/gait3d/experiment/stop`, {
        method: 'POST'
      });
      if (res.ok) {
        const data = await res.json();
        await refreshState();
        return data;
      }
    } catch (err) {
      console.error('Stop trial error:', err);
    }
    return null;
  };

  const fetchSignalAnalysis = async (mac: string) => {
    try {
      const res = await fetch(`${API_URL}/gait3d/signal/${mac}`);
      if (res.ok) {
        return await res.json();
      }
    } catch (err) {
      console.error("Signal analysis fetch error", err);
    }
    return null;
  };

  return {
    activities,
    metrics,
    sceneFrame,
    simulationEnabled,
    experiments,
    activeTrial,
    isRecording,
    samplesRecorded,
    isConnected,
    toggleSimulation,
    startTrial,
    stopTrial,
    fetchSignalAnalysis,
    refreshState
  };
}
