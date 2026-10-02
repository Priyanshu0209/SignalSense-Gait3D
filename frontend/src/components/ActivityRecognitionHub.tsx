import React from 'react';
import { GaitActivity } from '../hooks/useGait3D';
import { Activity, CheckCircle2, Shield, Play, Square } from 'lucide-react';

interface ActivityRecognitionHubProps {
  activities: GaitActivity[];
  topologyDevices?: any[];
}

export const ActivityRecognitionHub: React.FC<ActivityRecognitionHubProps> = ({ topologyDevices = [] }) => {
  // Use real topology data if available
  const activeDevice = topologyDevices.find(d => d.type === 'DEVICE' && d.status === 'ONLINE');
  const movState = activeDevice?.movement?.value || "Stationary";
  
  const getActivityBadge = (act: string) => {
    if (act === 'Moving') {
      return (
        <span className="flex items-center gap-2 px-4 py-1.5 rounded-xl bg-cyan-500/20 border border-cyan-500/40 text-cyan-300 text-base font-bold shadow-lg shadow-neon-blue">
          <Play size={18} className="text-cyan-400 animate-pulse" /> DEVICE IS MOVING
        </span>
      );
    }
    return (
      <span className="flex items-center gap-2 px-4 py-1.5 rounded-xl bg-background-secondary/80 border border-border text-text-muted text-base font-bold">
        <Square size={18} className="text-text-muted" /> DEVICE IS STATIONARY
      </span>
    );
  };

  return (
    <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-6">
      
      {/* Primary Classification Dashboard */}
      <div className="md:col-span-2 glass-panel p-6 rounded-2xl border border-border flex flex-col justify-between relative overflow-hidden">
        <div className="flex items-center justify-between border-b border-border/80 pb-4">
          <div>
            <h3 className="text-sm font-bold tracking-widest text-text-primary flex items-center gap-2">
              <Activity className="text-cyan-400" size={18} /> BASIC MOVEMENT TRACKING (RSSI)
            </h3>
            <p className="text-xs text-text-muted font-mono mt-0.5">Variance-based motion detection (Option A)</p>
          </div>
          {getActivityBadge(movState)}
        </div>

        <div className="my-6">
           <div className="p-4 rounded-xl bg-background-secondary/40 border border-border">
             <p className="text-sm text-text-muted mb-2 font-mono">
               <strong>Status:</strong> Tracking general room-level movement and proximity using wireless signals.
             </p>
           </div>
        </div>

        <div className="pt-4 border-t border-border/80 flex items-center justify-between text-xs text-text-muted font-mono">
          <div className="flex items-center gap-2">
            <CheckCircle2 size={16} className="text-emerald-400" />
            <span>Tracking Mode: <strong className="text-text-primary">Standard Wi-Fi RSSI</strong></span>
          </div>
          <span className="bg-background-secondary px-3 py-1 rounded-full border border-border text-[11px]">
            Target Node: <strong>{activeDevice?.mac_address || "None"}</strong>
          </span>
        </div>
      </div>

      {/* Feature Vector Breakdown Card */}
      <div className="glass-panel p-6 rounded-2xl border border-border flex flex-col justify-between">
        <div>
          <h4 className="text-sm font-bold tracking-widest text-text-primary flex items-center gap-2 pb-3 border-b border-border">
            <Shield className="text-purple-400" size={16} /> EXTRACTED HAR FEATURES
          </h4>
          <p className="text-xs text-text-muted mt-2 leading-relaxed">
            Time-domain variance computed over sliding Wi-Fi RSSI windows.
          </p>

          <div className="mt-5 space-y-4 font-mono text-xs">
            <div className="flex justify-between items-center bg-background-secondary/80 px-4 py-2.5 rounded-xl border border-border/80">
              <span className="text-text-muted">Motion State:</span>
              <strong className={movState === "Moving" ? "text-cyan-300" : "text-text-muted"}>{movState}</strong>
            </div>
            <div className="flex justify-between items-center bg-background-secondary/80 px-4 py-2.5 rounded-xl border border-border/80 opacity-50">
              <span className="text-text-muted">Dominant Freq (FFT):</span>
              <strong className="text-amber-300 text-sm">N/A (RSSI Mode)</strong>
            </div>
            <div className="flex justify-between items-center bg-background-secondary/80 px-4 py-2.5 rounded-xl border border-border/80 opacity-50">
              <span className="text-text-muted">Zero Crossing Rate:</span>
              <strong className="text-purple-300 text-sm">N/A (RSSI Mode)</strong>
            </div>
            <div className="flex justify-between items-center bg-background-secondary/80 px-4 py-2.5 rounded-xl border border-border/80 opacity-50">
              <span className="text-text-muted">Spectral Entropy:</span>
              <strong className="text-blue-300 text-sm">N/A (RSSI Mode)</strong>
            </div>
          </div>
        </div>

        <div className="mt-6 text-[11px] text-text-muted font-mono text-center border-t border-border/60 pt-3">
          SignalSense-Gait3D Basic Movement Engine
        </div>
      </div>

    </div>
  );
};
