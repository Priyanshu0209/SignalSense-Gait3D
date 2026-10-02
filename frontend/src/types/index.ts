export type SignalClassification = "Excellent" | "Good" | "Weak" | "Critical" | "Disconnected";
export type DistanceClassification = "Near" | "Medium" | "Far" | "Very Far" | "Disconnected";
export type SignalTrend = "Improving" | "Stable" | "Weakening" | "Rapid Drop" | "Fluctuating" | "None";

export interface AnimationState {
  color: string;
  pulse_speed: string;
  glow_intensity: string;
}

export interface DeviceState {
  mac: string;
  hostname: string | null;
  ip: string | null;
  manufacturer: string | null;
  rssi: number | null;
  signal: SignalClassification;
  distance: DistanceClassification;
  trend: SignalTrend;
  animation: AnimationState;
  status: "online" | "offline";
  connection_duration: number;
  timestamp: string;
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

export interface DashboardSummary {
  total_devices: number;
  online_devices: number;
  offline_devices: number;
}
