import React from 'react';
import { Activity, Server, Cpu, Wifi, Clock, Play, Square, RefreshCw } from 'lucide-react';

export const SystemHealthView: React.FC<{ opsState: any }> = ({ opsState }) => {
  const { metrics, services, controlService } = opsState;

  if (!metrics || !services) {
    return <div className="h-full flex items-center justify-center text-yellow-500 font-mono animate-pulse">CONNECTING TO METRIC ENGINE...</div>;
  }

  const srvList = Object.entries(services);

  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-2">
          <Activity className="text-yellow-500" /> System Health & Performance
        </h2>
        <p className="text-text-muted text-sm">Live hardware utilization, throughput, and service status.</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-4 gap-6">
        <div className="glass-panel p-5 border-t-2 border-blue-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-xs font-bold text-text-muted">CPU USAGE</p>
            <Cpu size={14} className="text-blue-500" />
          </div>
          <p className="text-2xl font-light text-text-primary">{metrics.cpu_usage}%</p>
          <div className="w-full bg-card h-1 mt-3 rounded overflow-hidden">
            <div className="bg-blue-500 h-full transition-all" style={{width: `${metrics.cpu_usage}%`}} />
          </div>
        </div>
        
        <div className="glass-panel p-5 border-t-2 border-purple-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-xs font-bold text-text-muted">RAM USAGE</p>
            <Server size={14} className="text-purple-500" />
          </div>
          <p className="text-2xl font-light text-text-primary">{metrics.ram_usage}%</p>
          <div className="w-full bg-card h-1 mt-3 rounded overflow-hidden">
            <div className="bg-purple-500 h-full transition-all" style={{width: `${metrics.ram_usage}%`}} />
          </div>
        </div>

        <div className="glass-panel p-5 border-t-2 border-green-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-xs font-bold text-text-muted">API LATENCY</p>
            <Clock size={14} className="text-green-500" />
          </div>
          <p className="text-2xl font-light text-text-primary">{metrics.api_latency_ms} <span className="text-sm font-mono text-text-muted">ms</span></p>
        </div>

        <div className="glass-panel p-5 border-t-2 border-orange-500">
          <div className="flex justify-between items-start mb-2">
            <p className="text-xs font-bold text-text-muted">NETWORK I/O</p>
            <Wifi size={14} className="text-orange-500" />
          </div>
          <p className="text-2xl font-light text-text-primary">{metrics.network_throughput} <span className="text-sm font-mono text-text-muted">MB/s</span></p>
        </div>
      </div>

      {/* Service Manager */}
      <div className="glass-panel overflow-hidden">
        <div className="p-5 border-b border-border flex justify-between items-center bg-card">
          <h3 className="font-bold text-text-primary flex items-center gap-2">
            <Server size={18} className="text-yellow-500" /> Service Manager
          </h3>
          <p className="text-xs font-mono text-text-muted">UPTIME: {Math.floor(metrics.system_uptime)}s</p>
        </div>
        <table className="w-full text-left text-sm text-text-primary">
          <thead className="bg-card text-text-muted text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4 w-1/3">Service Node</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4">Node Uptime</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-foreground/5">
            {srvList.map(([name, data]: [string, any]) => (
              <tr key={name} className="hover:bg-foreground/5 transition-colors">
                <td className="px-6 py-4 font-bold text-text-primary">{name}</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-[10px] font-bold tracking-wider uppercase ${
                    data.status === 'Running' || data.status === 'Connected' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 
                    data.status === 'Stopped' ? 'bg-red-500/10 text-red-400 border border-red-500/20' : 
                    'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20 animate-pulse'
                  }`}>
                    {data.status}
                  </span>
                </td>
                <td className="px-6 py-4 font-mono text-xs">{data.uptime > 0 ? `${data.uptime.toFixed(1)}s` : '-'}</td>
                <td className="px-6 py-4 text-right">
                  <div className="flex justify-end gap-2">
                    {data.status !== 'Running' && data.status !== 'Connected' && (
                      <button onClick={() => controlService(name, 'Start')} className="p-1.5 bg-green-500/20 hover:bg-green-500/40 text-green-400 rounded transition-colors"><Play size={14} /></button>
                    )}
                    {(data.status === 'Running' || data.status === 'Connected') && (
                      <button onClick={() => controlService(name, 'Stop')} className="p-1.5 bg-red-500/20 hover:bg-red-500/40 text-red-400 rounded transition-colors"><Square size={14} /></button>
                    )}
                    <button onClick={() => controlService(name, 'Restart')} className="p-1.5 bg-card-hover hover:bg-card-hover text-text-primary rounded transition-colors"><RefreshCw size={14} /></button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
