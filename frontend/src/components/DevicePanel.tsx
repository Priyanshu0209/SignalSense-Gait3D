import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ConnectedDevice, MetricStatus } from '../hooks/useNetworkData';
import { X, Smartphone, Laptop, Tv, Cpu, Wifi, Activity, Navigation, Database, BrainCircuit } from 'lucide-react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface DevicePanelProps {
  device: ConnectedDevice | null;
  onClose: () => void;
  onExplain?: () => void;
}

const getDeviceIcon = (type?: string) => {
  if (!type) return <Wifi size={32} className="text-blue-400" />;
  const t = type.toLowerCase();
  if (t.includes('phone') || t.includes('mobile')) return <Smartphone size={32} className="text-green-400" />;
  if (t.includes('laptop') || t.includes('pc') || t.includes('mac')) return <Laptop size={32} className="text-purple-400" />;
  if (t.includes('tv')) return <Tv size={32} className="text-yellow-400" />;
  if (t.includes('iot')) return <Cpu size={32} className="text-orange-400" />;
  return <Wifi size={32} className="text-blue-400" />;
};

const Tag = ({ status, source, confidence }: { status?: MetricStatus, source?: string, confidence?: number }) => {
  if (!status) return null;
  let bg = 'bg-slate-500/20';
  let border = 'border-border';
  let text = 'text-text-muted';
  
  if (status === 'REAL') {
    bg = 'bg-green-500/20'; border = 'border-green-500/30'; text = 'text-green-400';
  } else if (status === 'ESTIMATED') {
    bg = 'bg-yellow-500/20'; border = 'border-yellow-500/30'; text = 'text-yellow-400';
  }

  return (
    <div className="group relative inline-block">
      <span className={`text-[8px] px-1.5 py-0.5 rounded border uppercase tracking-widest ml-2 align-middle cursor-help ${bg} ${border} ${text}`}>
        {status}
      </span>
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block w-48 p-2 bg-card border border-border rounded shadow-2xl z-50 text-[10px] text-text-primary">
        <p className="mb-1"><strong className="text-text-muted">Source:</strong> {source || 'Unknown'}</p>
        <p><strong className="text-text-muted">Confidence:</strong> {confidence ? `${confidence.toFixed(0)}%` : 'N/A'}</p>
      </div>
    </div>
  );
};

export const DevicePanel: React.FC<DevicePanelProps> = ({ device, onClose, onExplain }) => {
  if (!device) return null;

  const hasRssi = device.current_rssi?.value !== null && device.current_rssi?.value !== undefined;
  const historyData = hasRssi ? Array.from({ length: 20 }, () => device.current_rssi.value! + (Math.random() * 6 - 3)) : [];
  
  const chartData = {
    labels: Array.from({ length: 20 }, (_, index) => `-${20 - index}s`),
    datasets: [
      {
        fill: true,
        label: 'RSSI (dBm)',
        data: historyData,
        borderColor: hasRssi ? 'rgba(59, 130, 246, 0.8)' : 'rgba(100, 116, 139, 0.4)',
        backgroundColor: hasRssi ? 'rgba(59, 130, 246, 0.1)' : 'rgba(100, 116, 139, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { mode: 'index' as const, intersect: false },
    },
    scales: {
      y: { grid: { color: 'rgba(255,255,255,0.05)' }, min: -100, max: -30 },
      x: { grid: { display: false } },
    },
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ x: 450, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 450, opacity: 0 }}
        transition={{ type: 'spring', damping: 25, stiffness: 200 }}
        className="fixed top-0 right-0 h-full w-[450px] glass-panel border-r-0 rounded-r-none z-50 flex flex-col shadow-2xl bg-card backdrop-blur-3xl"
      >
        <div className="p-6 border-b border-border flex justify-between items-center bg-background-secondary/50">
          <div className="flex items-center gap-4">
            <div className="p-3 rounded-xl bg-card border border-border shadow-inner">
              {getDeviceIcon(device.device_type)}
            </div>
            <div>
              <h3 className="text-lg font-bold text-text-primary leading-tight flex items-center">
                {device.hostname || 'Unknown Device'}
              </h3>
              <p className="text-xs text-text-muted">{device.manufacturer || 'Unknown Vendor'}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-foreground/10 rounded-full transition-colors text-text-muted hover:text-text-primary">
            <X size={20} />
          </button>
        </div>

        <div className="p-6 flex-grow overflow-y-auto custom-scrollbar space-y-6">
          
          <div className="grid grid-cols-2 gap-4">
            <InfoCard label="IP Address" value={device.ip_address} />
            <InfoCard label="MAC Address" value={device.mac_address} />
            <InfoCard label="Upload" value={`${device.tx_rate?.toFixed(1) || 0} Mbps`} />
            <InfoCard label="Download" value={`${device.rx_rate?.toFixed(1) || 0} Mbps`} />
          </div>

          {/* Spatial Awareness Section */}
          <div className="space-y-3">
            <h4 className="text-sm font-medium text-text-primary uppercase tracking-widest flex items-center gap-2">
              <Navigation size={14} className="text-blue-400" /> Spatial Telemetry
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-card p-4 rounded-xl border border-border relative overflow-hidden group hover:border-blue-500/30 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <p className="text-[10px] text-text-muted uppercase tracking-wider">Distance</p>
                  <Tag status={device.distance?.status} source={device.distance?.source} confidence={device.distance?.confidence} />
                </div>
                <div className="flex items-end gap-2">
                  <span className="text-2xl font-bold text-text-primary">
                    {device.distance?.value !== null ? device.distance?.value?.toFixed(1) : '---'}
                  </span>
                  <span className="text-sm text-text-muted mb-1">m</span>
                </div>
              </div>
              
              <div className="bg-card p-4 rounded-xl border border-border relative overflow-hidden group hover:border-blue-500/30 transition-colors">
                <div className="flex justify-between items-start mb-2">
                  <p className="text-[10px] text-text-muted uppercase tracking-wider">Direction</p>
                  <Tag status={device.direction?.status} source={device.direction?.source} confidence={device.direction?.confidence} />
                </div>
                <div className="flex items-end gap-2">
                  <span className="text-2xl font-bold text-text-primary">
                    {device.direction?.value !== null ? `${device.direction?.value?.toFixed(0)}°` : 'N/A'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-card border border-border relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-purple-500 opacity-50" />
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-medium text-text-primary flex items-center gap-2">
                <Activity size={16} className={hasRssi ? "text-blue-400" : "text-text-muted"}/> Signal Strength
                <Tag status={device.current_rssi?.status} source={device.current_rssi?.source} confidence={device.current_rssi?.confidence} />
              </span>
              <span className={`text-sm font-bold ${!hasRssi ? 'text-text-muted' : device.current_rssi.value! > -60 ? 'text-green-400' : device.current_rssi.value! > -80 ? 'text-yellow-400' : 'text-red-400'}`}>
                {hasRssi ? `${device.current_rssi.value} dBm` : 'N/A'}
              </span>
            </div>
            <div className="h-40 w-full relative">
              {!hasRssi && (
                <div className="absolute inset-0 flex items-center justify-center z-10">
                  <span className="text-text-muted text-sm font-medium bg-card px-3 py-1 rounded backdrop-blur-sm border border-border">Waiting for Signal...</span>
                </div>
              )}
              <Line options={chartOptions} data={chartData} className={!hasRssi ? 'opacity-30' : ''} />
            </div>
          </div>

          <div className="flex gap-2">
            <button 
              onClick={onExplain}
              className="flex-1 bg-purple-600/20 hover:bg-purple-600/40 text-purple-400 border border-purple-500/30 py-2 rounded-lg text-sm font-bold tracking-widest transition-colors flex items-center justify-center gap-2"
            >
              <BrainCircuit size={16} /> EXPLAIN AI
            </button>
            <button className="flex-1 bg-red-500/10 hover:bg-red-500/20 text-red-500 border border-red-500/20 py-2 rounded-lg text-sm font-bold tracking-widest transition-colors">
              BLOCK
            </button>
          </div>

          <div className="space-y-3">
            <h4 className="text-sm font-medium text-text-primary uppercase tracking-widest flex items-center gap-2">
              <Database size={14} className="text-blue-400" /> Advanced Metrics
            </h4>
            <div className="bg-card rounded-xl p-4 space-y-3 text-sm border border-border">
              <div className="flex justify-between items-center">
                <span className="text-text-muted">Movement State</span>
                <div className="flex items-center gap-2">
                  <Tag status={device.movement?.status} source={device.movement?.source} confidence={device.movement?.confidence} />
                  <span className="text-text-primary font-medium">{device.movement?.value || 'Unknown'}</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-text-muted">Activity Score</span>
                <span className="text-text-primary font-mono">{device.activity_score?.toFixed(0) || 0}/100</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-text-muted">Uptime</span>
                <span className="text-text-primary font-mono">{device.connection_duration ? Math.floor(device.connection_duration/60) : 0} m</span>
              </div>
            </div>
          </div>

        </div>
      </motion.div>
    </AnimatePresence>
  );
};

const InfoCard = ({ label, value }: { label: string, value: string }) => (
  <div className="bg-card p-4 rounded-xl border border-border hover:border-blue-500/20 transition-colors group">
    <p className="text-[10px] text-text-muted uppercase tracking-wider mb-1.5 group-hover:text-blue-400 transition-colors">{label}</p>
    <p className="text-sm text-text-primary font-medium truncate font-mono">{value}</p>
  </div>
);
