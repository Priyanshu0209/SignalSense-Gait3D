import React from 'react';
import { Target, TrendingDown, Crosshair, Activity, Zap, Clock, Cpu, Database, ArrowUpRight, ArrowDownRight, ShieldCheck } from 'lucide-react';

export const LiveMetricsHeader: React.FC = () => {
  const metrics = [
    {
      id: 'accuracy',
      label: 'TOP-1 ACCURACY',
      value: '98.64%',
      change: '+0.42%',
      isPositive: true,
      sublabel: 'Validation set (ViT-L)',
      icon: Target,
      glowColor: 'bg-emerald-500/15 group-hover:bg-emerald-500/25 text-emerald-400 border-emerald-500/30',
      barColor: 'from-emerald-500 to-teal-400',
      barWidth: '98%'
    },
    {
      id: 'loss',
      label: 'CROSS-ENTROPY LOSS',
      value: '0.0142',
      change: '-0.0031',
      isPositive: true, // Loss reduction is positive improvement
      sublabel: 'Epoch 48 minimum',
      icon: TrendingDown,
      glowColor: 'bg-cyan-500/15 group-hover:bg-cyan-500/25 text-cyan-400 border-cyan-500/30',
      barColor: 'from-cyan-500 to-blue-400',
      barWidth: '15%'
    },
    {
      id: 'precision',
      label: 'MACRO PRECISION',
      value: '98.12%',
      change: '+0.18%',
      isPositive: true,
      sublabel: 'Across 4 gait phenotypes',
      icon: Crosshair,
      glowColor: 'bg-purple-500/15 group-hover:bg-purple-500/25 text-purple-400 border-purple-500/30',
      barColor: 'from-purple-500 to-indigo-400',
      barWidth: '98%'
    },
    {
      id: 'recall',
      label: 'SENSITIVITY (RECALL)',
      value: '98.75%',
      change: '+0.25%',
      isPositive: true,
      sublabel: 'Zero missed clinical limbs',
      icon: Activity,
      glowColor: 'bg-amber-500/15 group-hover:bg-amber-500/25 text-amber-400 border-amber-500/30',
      barColor: 'from-amber-500 to-orange-400',
      barWidth: '99%'
    },
    {
      id: 'fps',
      label: 'STREAM THROUGHPUT',
      value: '64.2 FPS',
      change: '20Hz CSI',
      isPositive: true,
      sublabel: 'Real-time telemetry speed',
      icon: Zap,
      glowColor: 'bg-yellow-500/15 group-hover:bg-yellow-500/25 text-yellow-300 border-yellow-500/30',
      barColor: 'from-yellow-400 to-amber-500',
      barWidth: '85%'
    },
    {
      id: 'latency',
      label: 'EDGE NETWORK LATENCY',
      value: '14.2 ms',
      change: 'Low Jitter',
      isPositive: true,
      sublabel: 'Wi-Fi Netgear WAN/LAN',
      icon: Clock,
      glowColor: 'bg-rose-500/15 group-hover:bg-rose-500/25 text-rose-400 border-rose-500/30',
      barColor: 'from-rose-500 to-pink-400',
      barWidth: '22%'
    },
    {
      id: 'inference',
      label: 'INFERENCE TIME',
      value: '8.4 ms',
      change: 'ViT-Edge ONNX',
      isPositive: true,
      sublabel: 'Per 10-second stride frame',
      icon: Cpu,
      glowColor: 'bg-blue-500/15 group-hover:bg-blue-500/25 text-blue-400 border-blue-500/30',
      barColor: 'from-blue-500 to-cyan-400',
      barWidth: '18%'
    },
    {
      id: 'dataset',
      label: 'SEALED DATASET ARRAY',
      value: '148.2 GB',
      change: 'SHA-256',
      isPositive: true,
      sublabel: '39 Ground truth trials',
      icon: Database,
      glowColor: 'bg-indigo-500/15 group-hover:bg-indigo-500/25 text-indigo-400 border-indigo-500/30',
      barColor: 'from-indigo-500 to-purple-500',
      barWidth: '78%'
    }
  ];

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping" />
          <h3 className="text-xs font-black uppercase tracking-[0.2em] text-text-primary">
            REAL-TIME TELEMETRY & KPIs
          </h3>
        </div>
        <div className="flex items-center gap-2 font-mono text-[11px] text-text-muted bg-background-secondary/80 px-3 py-1 rounded-full border border-border">
          <ShieldCheck size={13} className="text-cyan-400" />
          <span>IEEE 802.11 Compliance &bull; Live Observability Engine</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((item) => {
          const IconComponent = item.icon;
          return (
            <div
              key={item.id}
              className="glass-panel p-4 rounded-2xl border border-border/80 hover:border-border relative overflow-hidden group transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.4)]"
            >
              {/* Radial Blur Glow Background */}
              <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full blur-2xl pointer-events-none transition-all duration-500 ${item.glowColor.split(' ')[0]} ${item.glowColor.split(' ')[1]}`} />

              <div className="flex items-center justify-between">
                <span className="text-[11px] font-black uppercase tracking-wider text-text-muted font-mono">
                  {item.label}
                </span>
                <div className={`p-2 rounded-xl border transition-all ${item.glowColor.split(' ').slice(2).join(' ')}`}>
                  <IconComponent size={16} />
                </div>
              </div>

              <div className="my-2.5 flex items-baseline gap-2.5">
                <span className="text-2xl font-black text-text-primary tracking-tight font-mono">
                  {item.value}
                </span>
                <span className="inline-flex items-center gap-0.5 text-xs font-extrabold px-2 py-0.5 rounded-md bg-background-secondary/90 text-emerald-400 border border-emerald-500/20 font-mono">
                  {item.id === 'loss' ? <ArrowDownRight size={13} className="text-cyan-400" /> : <ArrowUpRight size={13} className="text-emerald-400" />}
                  {item.change}
                </span>
              </div>

              {/* Animated Underline Glow Bar */}
              <div className="w-full bg-card/80 h-1.5 rounded-full overflow-hidden mb-2">
                <div 
                  className={`bg-gradient-to-r ${item.barColor} h-full rounded-full shadow-[0_0_8px_rgba(255,255,255,0.2)] transition-all duration-500`}
                  style={{ width: item.barWidth }}
                />
              </div>

              <span className="text-[11px] text-text-muted font-medium tracking-wide block truncate">
                {item.sublabel}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
