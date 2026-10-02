import React from 'react';
import { RouterStatus } from '../hooks/useNetworkData';
import { Shield, Clock, HardDrive, Wifi, Activity, X, Server } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface RouterInfoProps {
  isOpen: boolean;
  onClose: () => void;
  status: RouterStatus | null;
}

export const RouterInfo: React.FC<RouterInfoProps> = ({ isOpen, onClose, status }) => {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-background-primary/80 backdrop-blur-md z-50 flex items-center justify-center p-4"
        onClick={onClose}
      >
        <motion.div 
          initial={{ scale: 0.95, opacity: 0, y: 20 }}
          animate={{ scale: 1, opacity: 1, y: 0 }}
          exit={{ scale: 0.95, opacity: 0, y: 20 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          onClick={(e) => e.stopPropagation()}
          className="relative w-full max-w-2xl bg-card/90 backdrop-blur-2xl border border-border rounded-3xl shadow-glass overflow-hidden"
        >
          {/* Animated Background Glow */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[120%] h-32 bg-accent-primary/20 blur-[80px] -z-10 pointer-events-none" />

          <div className="flex items-center justify-between p-6 border-b border-border">
            <div className="flex items-center gap-4">
              <div className="p-2.5 bg-accent-primary/20 rounded-xl border border-accent-primary/30 text-accent-primary shadow-neon-blue">
                <Server size={24} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-text-primary tracking-tight">System Gateway Details</h2>
                <p className="text-xs text-text-muted font-mono tracking-widest uppercase">Hardware Telemetry Profile</p>
              </div>
            </div>
            <button 
              onClick={onClose}
              className="p-2 text-text-muted hover:text-text-primary hover:bg-foreground/5 rounded-full transition-colors"
            >
              <X size={24} />
            </button>
          </div>

          <div className="p-8 space-y-6">
            {!status ? (
              <div className="flex flex-col items-center justify-center py-12 text-text-muted gap-4">
                <Activity size={32} className="animate-pulse opacity-50" />
                <span className="text-sm font-bold tracking-widest uppercase">No Active Gateway Payload Detected</span>
              </div>
            ) : (
              <div className="grid grid-cols-2 gap-4">
                <InfoItem label="Connection Method" value={status.adapter_type || "Unknown"} icon={<Wifi size={18} />} color="text-accent-secondary" />
                <InfoItem label="Adapter Interface" value={status.adapter_type || "Unknown"} icon={<Activity size={18} />} color="text-accent-primary" />
                <InfoItem label="Authentication Lock" value={status.connection_status === "Connected" ? "Authenticated" : "Failed"} icon={<Shield size={18} />} color="text-status-success" />
                <InfoItem label="Last Sequence Sync" value={new Date(status.timestamp).toLocaleTimeString()} icon={<Clock size={18} />} color="text-text-secondary" />
                <InfoItem label="Data Polling Rate" value="1.0s (High Frequency)" icon={<Clock size={18} />} color="text-text-secondary" />
                <InfoItem label="Firmware Matrix" value={status.firmware_version || "N/A"} icon={<HardDrive size={18} />} color="text-text-secondary" />
                <InfoItem label="Hardware Vendor" value={status.vendor || 'Unknown'} icon={<HardDrive size={18} />} color="text-text-secondary" />
                <InfoItem label="Device Model" value={status.router_model || 'Unknown'} icon={<HardDrive size={18} />} color="text-text-secondary" />
              </div>
            )}
          </div>
          
          <div className="p-6 border-t border-border bg-background-primary/40 flex items-center justify-between">
            <div className="text-[10px] font-bold text-text-muted tracking-widest uppercase flex items-center gap-2">
              <Shield size={12} className="text-accent-secondary" />
              Adapter strictly manages real-time isolated network telemetry.
            </div>
            <button onClick={onClose} className="px-6 py-2 rounded-full bg-foreground/5 hover:bg-foreground/10 text-xs font-bold text-text-primary tracking-widest uppercase transition-colors">
              Close Panel
            </button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const InfoItem = ({ label, value, icon, color }: { label: string, value: string, icon: React.ReactNode, color: string }) => (
  <div className="group bg-background-primary/40 rounded-2xl p-4 border border-border flex items-start gap-4 hover:bg-card-hover transition-colors duration-300">
    <div className={`mt-0.5 p-2 bg-foreground/5 rounded-lg group-hover:bg-foreground/10 transition-colors ${color}`}>
      {icon}
    </div>
    <div>
      <p className="text-text-muted text-[10px] font-bold tracking-widest uppercase mb-1">{label}</p>
      <p className="text-text-primary text-sm font-semibold font-mono">{value}</p>
    </div>
  </div>
);
