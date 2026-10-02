import React from 'react';
import { RouterStatus } from '../hooks/useNetworkData';
import { Activity, Cpu, HardDrive, Wifi, Zap, Server } from 'lucide-react';

interface RouterDashboardProps {
  status: RouterStatus | null;
  onRunDiagnostics: () => void;
}

export const RouterDashboard: React.FC<RouterDashboardProps> = ({ status, onRunDiagnostics }) => {
  if (!status) return (
    <div className="h-full flex items-center justify-center p-6 bg-card/20 rounded-3xl border border-border">
      <div className="flex flex-col items-center gap-4">
        <Activity size={32} className="text-accent-primary animate-pulse" />
        <div className="text-text-muted font-bold tracking-widest text-sm">INITIALIZING TELEMETRY...</div>
      </div>
    </div>
  );

  const formatUptime = (seconds: number) => {
    const d = Math.floor(seconds / (3600*24));
    const h = Math.floor(seconds % (3600*24) / 3600);
    const m = Math.floor(seconds % 3600 / 60);
    return `${d}d ${h}h ${m}m`;
  };

  const isConnected = status.connection_status === 'Connected';

  return (
    <div className="h-full flex flex-col p-6 bg-gradient-to-b from-card/40 to-background-primary/40">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-accent-primary/20 rounded-xl border border-accent-primary/30 text-accent-primary shadow-neon-blue">
            <Server size={20} />
          </div>
          <div>
            <h2 className="text-lg font-bold text-text-primary tracking-wide">GATEWAY</h2>
            <p className="text-xs text-text-muted font-mono">{status.router_model}</p>
          </div>
        </div>
        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border shadow-sm ${
          isConnected ? 'bg-status-success/10 border-status-success/30 text-status-success shadow-neon-green' : 'bg-status-error/10 border-status-error/30 text-status-error shadow-neon-red'
        }`}>
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-status-success animate-pulse' : 'bg-status-error'}`} />
          <span className="text-xs font-bold tracking-widest uppercase">{status.connection_status || 'OFFLINE'}</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <KpiCard 
          icon={<Cpu size={16} />} 
          label="CPU LOAD" 
          value={status.capabilities.supports_cpu && status.cpu_usage !== null ? `${status.cpu_usage.toFixed(1)}%` : '--'} 
          color="text-accent-primary"
        />
        <KpiCard 
          icon={<HardDrive size={16} />} 
          label="MEMORY" 
          value={status.capabilities.supports_memory && status.memory_usage !== null ? `${status.memory_usage.toFixed(1)}%` : '--'} 
          color="text-accent-secondary"
        />
        <KpiCard 
          icon={<Wifi size={16} />} 
          label="BANDWIDTH" 
          value={`${status.bandwidth_mbps || 0} MBPS`} 
          color="text-status-success"
        />
        <KpiCard 
          icon={<Zap size={16} />} 
          label="LATENCY" 
          value={`${status.latency_ms?.toFixed(1) || 0} MS`} 
          color="text-status-warning"
        />
      </div>

      <div className="flex-grow space-y-3 overflow-y-auto custom-scrollbar pr-2">
        <div className="text-xs font-bold text-text-muted tracking-widest uppercase mb-4 mt-2">Network Diagnostics</div>
        <ListRow label="Internet Status" value={status.internet_status} />
        <ListRow label="Gateway IP" value={status.gateway_ip} />
        <ListRow label="WAN Interface" value={status.wan_ip || 'N/A'} />
        <ListRow label="Frequency Band" value={status.frequency || 'N/A'} />
        <ListRow label="Active Channel" value={status.wifi_channel?.toString() || 'Auto'} />
        <ListRow label="Packet Loss" value={`${status.packet_loss_percent?.toFixed(2) || 0}%`} highlight={(status.packet_loss_percent ?? 0) > 5} />
        <ListRow label="DNS Resolver" value={status.dns_status || 'OK'} />
        <ListRow label="System Uptime" value={formatUptime(status.uptime_seconds)} />
      </div>

      <div className="mt-6 pt-4 border-t border-border">
        <button 
          onClick={onRunDiagnostics}
          className="w-full relative group overflow-hidden rounded-xl bg-accent-primary/10 border border-accent-primary/30 p-3 transition-all duration-300 hover:shadow-neon-blue hover:bg-accent-primary/20 hover:-translate-y-0.5"
        >
          <div className="absolute inset-0 w-0 bg-accent-primary/10 transition-all duration-500 ease-out group-hover:w-full" />
          <span className="relative flex items-center justify-center gap-2 text-accent-primary font-bold text-sm tracking-widest">
            <Activity size={16} /> INITIALIZE DIAGNOSTICS
          </span>
        </button>
      </div>
    </div>
  );
};

const KpiCard = ({ icon, label, value, color }: { icon: React.ReactNode, label: string, value: string, color: string }) => (
  <div className="flex flex-col gap-2 p-4 bg-background-primary/60 border border-border rounded-2xl transition-all duration-300 hover:bg-card-hover/80 hover:border-border group">
    <div className={`flex items-center gap-2 ${color}`}>
      <div className="p-1.5 bg-foreground/5 rounded-lg group-hover:bg-foreground/10 transition-colors">
        {icon}
      </div>
      <span className="text-[10px] font-bold tracking-widest uppercase text-text-muted">{label}</span>
    </div>
    <div className="text-xl font-bold text-text-primary tracking-tight font-mono">{value}</div>
  </div>
);

const ListRow = ({ label, value, highlight = false }: { label: string, value: string, highlight?: boolean }) => (
  <div className="flex items-center justify-between py-1">
    <span className="text-xs text-text-muted">{label}</span>
    <span className={`text-xs font-medium font-mono ${highlight ? 'text-status-error' : 'text-text-primary'}`}>{value}</span>
  </div>
);
