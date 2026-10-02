import React from 'react';
import { RouterStatus, ConnectedDevice } from '../hooks/useNetworkData';
import { Activity, Users, Zap, Signal, HardDrive, ShieldCheck } from 'lucide-react';

interface NetworkInsightsProps {
  routerStatus: RouterStatus | null;
  devices: ConnectedDevice[];
}

export const NetworkInsights: React.FC<NetworkInsightsProps> = ({ routerStatus, devices }) => {
  if (!routerStatus) return null;

  const onlineDevices = devices.filter(d => d.online_status).length;
  
  let totalTx = 0;
  let totalRx = 0;
  devices.forEach(d => {
    totalTx += (d.tx_rate || 0);
    totalRx += (d.rx_rate || 0);
  });
  const currentThroughput = totalTx + totalRx;

  // Simple heuristic for Network Score
  let score = 100;
  if (routerStatus.cpu_usage && routerStatus.cpu_usage > 80) score -= 10;
  if (routerStatus.memory_usage && routerStatus.memory_usage > 80) score -= 10;
  if (routerStatus.packet_loss_percent && routerStatus.packet_loss_percent > 1) score -= 20;

  return (
    <div className="w-full flex justify-center gap-4 py-4 z-20 pointer-events-none">
      <InsightCard 
        icon={<ShieldCheck size={16} className="text-green-400" />} 
        label="Network Score" 
        value={`${score}/100`} 
      />
      <InsightCard 
        icon={<Users size={16} className="text-blue-400" />} 
        label="Active Devices" 
        value={`${onlineDevices}`} 
      />
      <InsightCard 
        icon={<Activity size={16} className="text-purple-400" />} 
        label="Throughput" 
        value={`${currentThroughput.toFixed(0)} Mbps`} 
      />
      <InsightCard 
        icon={<Zap size={16} className="text-yellow-400" />} 
        label="Latency" 
        value={`${routerStatus.latency_ms || '< 1'} ms`} 
      />
      <InsightCard 
        icon={<Signal size={16} className="text-orange-400" />} 
        label="Est. Coverage" 
        value="Good" 
      />
      <InsightCard 
        icon={<HardDrive size={16} className="text-cyan-400" />} 
        label="Router Load" 
        value={`${routerStatus.cpu_usage || 0}%`} 
      />
    </div>
  );
};

const InsightCard = ({ icon, label, value }: { icon: React.ReactNode, label: string, value: string }) => (
  <div className="bg-card backdrop-blur-xl border border-border rounded-2xl px-4 py-2 flex items-center gap-3 shadow-lg pointer-events-auto hover:bg-card transition-colors cursor-default">
    <div className="p-2 bg-foreground/5 rounded-full border border-border">
      {icon}
    </div>
    <div className="flex flex-col">
      <span className="text-[10px] text-text-muted uppercase tracking-widest">{label}</span>
      <span className="text-sm font-bold text-text-primary tracking-wide">{value}</span>
    </div>
  </div>
);
