import React from 'react';
import { ConnectedDevice, RouterStatus } from '../hooks/useNetworkData';
import { FileJson, FileText, BarChart3, Activity, ArrowUpRight, ArrowDownRight, Zap } from 'lucide-react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

interface AnalyticsDashboardProps {
  devices: ConnectedDevice[];
  routerStatus: RouterStatus | null;
}

export const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ devices, routerStatus }) => {
  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({ routerStatus, devices }, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "signalsense_export.json");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const handleExportCSV = () => {
    const headers = ["MAC", "IP", "Hostname", "Type", "Status", "Health", "Distance_m", "RSSI", "Traffic_Mbps"];
    const rows = devices.map(d => [
      d.mac_address, d.ip_address, d.hostname || "Unknown", d.device_type || "Unknown",
      d.online_status ? "Online" : "Offline", d.health_score || "N/A",
      d.distance?.value?.toFixed(2) || "N/A", d.current_rssi?.value || "N/A",
      ((d.tx_rate || 0) + (d.rx_rate || 0)).toFixed(2)
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + headers.join(",") + "\n" + rows.map(e => e.join(",")).join("\n");
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", encodeURI(csvContent));
    downloadAnchorNode.setAttribute("download", "signalsense_export.csv");
    document.body.appendChild(downloadAnchorNode);
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
  };

  const sortedDevices = [...devices].sort((a, b) => ((b.tx_rate || 0) + (b.rx_rate || 0)) - ((a.tx_rate || 0) + (a.rx_rate || 0))).slice(0, 5);
  
  const barChartData = {
    labels: sortedDevices.map(d => d.hostname || d.mac_address.substring(0,8)),
    datasets: [
      {
        label: 'Traffic (Mbps)',
        data: sortedDevices.map(d => (d.tx_rate || 0) + (d.rx_rate || 0)),
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
        borderRadius: 6,
        borderWidth: 0,
        hoverBackgroundColor: 'rgba(59, 130, 246, 1)',
      }
    ]
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        titleColor: '#fff',
        bodyColor: '#cbd5e1',
        borderColor: 'rgba(255,255,255,0.1)',
        borderWidth: 1,
        padding: 12,
        cornerRadius: 8,
      }
    },
    scales: {
      y: { 
        grid: { color: 'rgba(255,255,255,0.05)', borderDash: [4, 4] },
        ticks: { color: '#94a3b8', font: { family: 'monospace' } },
        border: { display: false }
      },
      x: { 
        grid: { display: false },
        ticks: { color: '#94a3b8', font: { family: 'Inter', size: 11 } },
        border: { display: false }
      },
    }
  };

  return (
    <div className="w-full h-full flex flex-col p-8 bg-transparent">
      
      <div className="flex justify-between items-end mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-accent-primary/20 rounded-xl border border-accent-primary/30 shadow-neon-blue">
              <Activity size={24} className="text-accent-primary" />
            </div>
            <h2 className="text-3xl font-bold text-text-primary tracking-tight">Analytics Center</h2>
          </div>
          <p className="text-text-muted text-sm tracking-wide">Enterprise Telemetry & Performance Aggregation</p>
        </div>

        <div className="flex gap-4">
          <button onClick={handleExportCSV} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-card border border-border hover:border-border hover:bg-card-hover text-text-primary text-sm font-semibold transition-all shadow-lg">
            <FileText size={18} className="text-accent-secondary" /> Export CSV
          </button>
          <button onClick={handleExportJSON} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-accent-primary text-text-primary text-sm font-semibold hover:bg-accent-primary/90 transition-all shadow-neon-blue border border-accent-primary/50">
            <FileJson size={18} /> Export JSON
          </button>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-8">
        <StatCard title="TOTAL CONNECTED" value={devices.filter(d=>d.online_status).length.toString()} suffix="Active" icon={<Zap size={20} className="text-status-warning" />} trend="+2" />
        <StatCard title="NETWORK THROUGHPUT" value={devices.reduce((acc, d) => acc + (d.tx_rate||0) + (d.rx_rate||0), 0).toFixed(1)} suffix="Mbps" icon={<Activity size={20} className="text-status-success" />} trend="+14.2%" />
        <StatCard title="COMPUTE UTILIZATION" value={`${(routerStatus?.cpu_usage || 0).toFixed(1)}`} suffix="%" icon={<BarChart3 size={20} className="text-accent-primary" />} trend="-1.5%" negative />
      </div>

      <div className="grid grid-cols-2 gap-8 flex-1 min-h-0">
        <div className="glass-card p-6 flex flex-col relative overflow-hidden">
          <div className="absolute top-0 right-0 w-64 h-64 bg-accent-primary/10 rounded-full blur-[80px] -z-10 translate-x-1/2 -translate-y-1/2 pointer-events-none" />
          <h3 className="text-sm font-bold text-text-muted tracking-widest uppercase mb-6 flex items-center gap-2">
            <Activity size={16} className="text-accent-primary" /> Top Bandwidth Consumers
          </h3>
          <div className="flex-1 min-h-0">
            <Bar data={barChartData} options={chartOptions} />
          </div>
        </div>

        <div className="glass-card p-0 flex flex-col overflow-hidden relative">
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-accent-secondary/10 rounded-full blur-[80px] -z-10 -translate-x-1/2 translate-y-1/2 pointer-events-none" />
          <div className="p-6 border-b border-border">
            <h3 className="text-sm font-bold text-text-muted tracking-widest uppercase">Client Health Matrix</h3>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 pt-0 mt-4">
            <table className="w-full text-left">
              <thead className="text-text-muted text-xs uppercase font-bold tracking-wider sticky top-0 bg-card/90 backdrop-blur-md pb-4 z-10">
                <tr>
                  <th className="pb-4 font-semibold">Device Identity</th>
                  <th className="pb-4 font-semibold">Health Score</th>
                  <th className="pb-4 font-semibold text-right">Distance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-foreground/5">
                {devices.map(d => (
                  <tr key={d.mac_address} className="hover:bg-foreground/5 transition-colors group">
                    <td className="py-4">
                      <div className="font-medium text-text-primary text-sm">{d.hostname || d.mac_address}</div>
                      <div className="text-xs text-text-muted font-mono">{d.ip_address}</div>
                    </td>
                    <td className="py-4">
                      <span className={`px-2.5 py-1 rounded-md text-[10px] uppercase font-bold tracking-widest border ${getHealthColor(d.health_score)}`}>
                        {d.health_score || 'N/A'}
                      </span>
                    </td>
                    <td className="py-4 text-right">
                      <div className="text-text-primary font-mono text-sm">{d.distance?.value?.toFixed(1) || '--'} m</div>
                      <div className="text-xs text-text-muted">{d.current_rssi?.value || '--'} dBm</div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, suffix, icon, trend, negative = false }: { title: string, value: string, suffix: string, icon: React.ReactNode, trend: string, negative?: boolean }) => (
  <div className="glass-card p-6 relative overflow-hidden flex flex-col justify-between">
    <div className="flex justify-between items-start mb-4">
      <div className="p-2.5 bg-foreground/5 rounded-xl border border-border">{icon}</div>
      <div className={`flex items-center gap-1 text-xs font-bold px-2 py-1 rounded-full bg-foreground/5 ${negative ? 'text-status-error' : 'text-status-success'}`}>
        {negative ? <ArrowDownRight size={14} /> : <ArrowUpRight size={14} />} {trend}
      </div>
    </div>
    <div>
      <div className="text-xs font-bold text-text-muted tracking-widest uppercase mb-1">{title}</div>
      <div className="flex items-baseline gap-2">
        <span className="text-4xl font-bold text-text-primary tracking-tight font-mono">{value}</span>
        <span className="text-sm text-text-muted font-medium">{suffix}</span>
      </div>
    </div>
  </div>
);

const getHealthColor = (score?: string) => {
  switch(score) {
    case 'Excellent': return 'bg-status-success/10 text-status-success border-status-success/30 shadow-[0_0_10px_rgba(34,197,94,0.1)]';
    case 'Good': return 'bg-accent-primary/10 text-accent-primary border-accent-primary/30 shadow-[0_0_10px_rgba(59,130,246,0.1)]';
    case 'Average': return 'bg-status-warning/10 text-status-warning border-status-warning/30 shadow-[0_0_10px_rgba(245,158,11,0.1)]';
    case 'Poor': return 'bg-status-error/10 text-status-error border-status-error/30 shadow-[0_0_10px_rgba(239,68,68,0.1)]';
    case 'Critical': return 'bg-status-error/20 text-status-error border-status-error/50 shadow-neon-red animate-pulse';
    default: return 'bg-foreground/5 text-text-muted border-border';
  }
};
