import React from 'react';
import { ReplayFrame } from '../hooks/useLocalization';
import { Target, Activity, Zap, Wifi } from 'lucide-react';

export const MetricsOverlay: React.FC<{ frame: ReplayFrame | null }> = ({ frame }) => {
  if (!frame) {
    return (
      <div className="glass-panel h-full flex flex-col items-center justify-center text-text-muted p-6 text-center">
        <Target size={48} className="mb-4 opacity-50" />
        <h3 className="font-bold text-lg text-text-primary mb-2">Metrics Overlay Offline</h3>
        <p className="text-sm">Load a dataset and start replay to view live prediction and ground truth metrics.</p>
      </div>
    );
  }

  // Derived metrics
  const relError = frame.gt_distance > 0 ? (frame.abs_error / frame.gt_distance) * 100 : 0;
  
  return (
    <div className="flex flex-col gap-4 h-full">
      {/* Ground Truth Overlay */}
      <div className="glass-panel p-5 border-l-4 border-green-500">
        <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
          <Target size={14} className="text-green-500" /> Ground Truth
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">DISTANCE</p>
            <p className="text-xl font-light text-text-primary">{frame.gt_distance.toFixed(2)}<span className="text-sm text-text-muted ml-1">m</span></p>
          </div>
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">DIRECTION</p>
            <p className="text-xl font-light text-text-primary">{frame.gt_direction}°</p>
          </div>
          <div className="col-span-2">
            <p className="text-xs font-bold text-text-muted mb-1">DEVICE MAC</p>
            <p className="text-sm font-mono text-text-primary">{frame.mac_address}</p>
          </div>
        </div>
      </div>

      {/* Prediction Overlay */}
      <div className="glass-panel p-5 border-l-4 border-red-500">
        <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
          <Activity size={14} className="text-red-500 animate-pulse" /> AI Prediction
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">EST. DISTANCE</p>
            <p className="text-xl font-light text-red-400">{frame.est_distance.toFixed(2)}<span className="text-sm text-text-muted ml-1">m</span></p>
          </div>
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">CONFIDENCE</p>
            <p className="text-xl font-light text-text-primary">{frame.confidence}%</p>
          </div>
        </div>
      </div>

      {/* Prediction Error */}
      <div className="glass-panel p-5 border-l-4 border-yellow-500">
        <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
          <Zap size={14} className="text-yellow-500" /> Live Error Analysis
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">ABSOLUTE ERROR</p>
            <p className="text-xl font-light text-yellow-400">{frame.abs_error.toFixed(2)}<span className="text-sm text-text-muted ml-1">m</span></p>
          </div>
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">RELATIVE ERROR</p>
            <p className="text-xl font-light text-text-primary">{relError.toFixed(1)}%</p>
          </div>
        </div>
      </div>

      {/* Live RSSI Monitor */}
      <div className="glass-panel p-5 flex-1">
        <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-4 flex items-center gap-2">
          <Wifi size={14} className="text-blue-500" /> Signal Telemetry
        </h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">RSSI</p>
            <p className="text-xl font-light text-blue-400">{frame.rssi} <span className="text-xs text-text-muted font-mono">dBm</span></p>
          </div>
          <div>
            <p className="text-xs font-bold text-text-muted mb-1">SNR</p>
            <p className="text-xl font-light text-text-primary">~35 <span className="text-xs text-text-muted font-mono">dB</span></p>
          </div>
        </div>
      </div>
    </div>
  );
};
