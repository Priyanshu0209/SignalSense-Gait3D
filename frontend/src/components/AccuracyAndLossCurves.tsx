import React, { useState } from 'react';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, TrendingDown, Target, Sparkles, Layers } from 'lucide-react';

// Generate realistic dummy telemetry over 50 epochs
const generateEpochData = () => {
  const data = [];
  for (let i = 1; i <= 50; i++) {
    
    // Smooth asymptotic accuracy convergence
    const vitAcc = Math.min(98.64, 78 + 20.64 * (1 - Math.exp(-i / 10)) + (Math.sin(i) * 0.25));
    const resnetAcc = Math.min(94.8, 72 + 22.8 * (1 - Math.exp(-i / 12)) + (Math.cos(i) * 0.35));
    const cnnAcc = Math.min(91.4, 65 + 26.4 * (1 - Math.exp(-i / 14)) + (Math.sin(i * 1.2) * 0.5));

    // Smooth exponential decay loss curves
    const trainLoss = Math.max(0.012, 0.85 * Math.exp(-i / 9) + (0.005 * Math.sin(i * 2)));
    const valLoss = Math.max(0.0142, 0.92 * Math.exp(-i / 10) + (0.006 * Math.cos(i * 1.5)));

    data.push({
      epoch: `Ep ${i}`,
      rawEpoch: i,
      vitAccuracy: Number(vitAcc.toFixed(2)),
      resnetAccuracy: Number(resnetAcc.toFixed(2)),
      cnnAccuracy: Number(cnnAcc.toFixed(2)),
      trainLoss: Number(trainLoss.toFixed(4)),
      valLoss: Number(valLoss.toFixed(4))
    });
  }
  return data;
};

const telemetryData = generateEpochData();

export const AccuracyAndLossCurves: React.FC = () => {
  const [selectedView, setSelectedView] = useState<'all' | 'best'>('all');

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background-secondary/95 border border-border p-3 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)] backdrop-blur-md text-xs font-mono">
          <p className="text-text-primary font-black border-b border-border pb-1 mb-2 uppercase tracking-wider">{label} Metrics Snapshot</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-6 py-0.5">
              <span className="flex items-center gap-2 font-semibold" style={{ color: entry.color }}>
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: entry.color }} />
                {entry.name}:
              </span>
              <span className="font-bold text-text-primary font-mono">
                {entry.value}{entry.name.toLowerCase().includes('accuracy') ? '%' : ''}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
      
      {/* Chart 1: Experiment Accuracy Trend */}
      <div className="glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)] transition-all">
        <div className="absolute -top-10 -right-10 w-48 h-48 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />
        
        <div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/80 pb-4 mb-4">
            <div>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-purple-400 flex items-center gap-2 font-mono">
                <Target size={15} /> COMPONENT 01 // ACCURACY CONVERGENCE
              </span>
              <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide flex items-center gap-2">
                Experiment Accuracy Trend <span className="text-xs font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">98.64% Peak</span>
              </h3>
            </div>

            <div className="flex items-center gap-1.5 bg-background-secondary/90 p-1 rounded-xl border border-border font-mono text-[11px]">
              <button 
                onClick={() => setSelectedView('all')} 
                className={`px-3 py-1 rounded-lg font-bold transition-all ${selectedView === 'all' ? 'bg-purple-600 text-text-primary shadow-lg shadow-purple-500/30' : 'text-text-muted hover:text-text-primary'}`}
              >
                Compare All
              </button>
              <button 
                onClick={() => setSelectedView('best')} 
                className={`px-3 py-1 rounded-lg font-bold transition-all ${selectedView === 'best' ? 'bg-purple-600 text-text-primary shadow-lg shadow-purple-500/30' : 'text-text-muted hover:text-text-primary'}`}
              >
                ViT Only
              </button>
            </div>
          </div>

          <p className="text-xs text-text-muted mb-4 flex items-center justify-between font-mono">
            <span>X-Axis: Epoch (1-50) &bull; Y-Axis: Validation Accuracy (%)</span>
            <span className="text-cyan-400 flex items-center gap-1"><Sparkles size={12} /> SOTA Transformer Architecture</span>
          </p>
        </div>

        <div className="w-full h-80 pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={telemetryData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="rawEpoch" stroke="#64748b" textAnchor="middle" tick={{ fill: '#94a3b8', fontSize: 11 }} domain={[1, 50]} />
              <YAxis stroke="#64748b" domain={[60, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(val) => `${val}%`} />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase' }} />
              
              {selectedView === 'all' && (
                <>
                  <Line type="monotone" dataKey="cnnAccuracy" name="CNN (Baseline)" stroke="#64748b" strokeWidth={2} dot={false} strokeDasharray="4 4" />
                  <Line type="monotone" dataKey="resnetAccuracy" name="ResNet-50" stroke="#06b6d4" strokeWidth={2.5} dot={false} />
                </>
              )}
              <Line type="monotone" dataKey="vitAccuracy" name="ViT-Gait3D-Large (Ours)" stroke="#a855f7" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: '#a855f7', stroke: '#fff', strokeWidth: 2 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span className="flex items-center gap-1.5 text-text-primary">
            <Layers size={14} className="text-purple-400" /> Multi-Layer Attention mapping achieving rapid convergence by Epoch 18.
          </span>
          <span className="text-purple-400 font-bold">TensorBoard Active</span>
        </div>
      </div>

      {/* Chart 2: Loss Curve */}
      <div className="glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)] transition-all">
        <div className="absolute -top-10 -right-10 w-48 h-48 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none" />

        <div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/80 pb-4 mb-4">
            <div>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-cyan-400 flex items-center gap-2 font-mono">
                <TrendingDown size={15} /> COMPONENT 02 // CROSS-ENTROPY MINIMIZATION
              </span>
              <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide flex items-center gap-2">
                Training & Validation Loss Curve <span className="text-xs font-mono text-cyan-300 bg-cyan-500/10 px-2 py-0.5 rounded-full border border-cyan-500/20">&nabla; 0.0142 Min</span>
              </h3>
            </div>
            
            <div className="text-right">
              <span className="text-[11px] font-mono text-text-muted block font-bold">SMOOTH ANIMATED SERIES</span>
              <span className="text-[10px] font-mono text-emerald-400 uppercase">No Overfitting Observed</span>
            </div>
          </div>

          <p className="text-xs text-text-muted mb-4 flex items-center justify-between font-mono">
            <span>Training Loss (Gradient Descent) vs. Validation Loss (Unseen Test)</span>
            <span className="text-purple-400">L2 Regularization Active</span>
          </p>
        </div>

        <div className="w-full h-80 pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={telemetryData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
              <defs>
                <linearGradient id="trainLossGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0}/>
                </linearGradient>
                <linearGradient id="valLossGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.5}/>
                  <stop offset="95%" stopColor="#06b6d4" stopOpacity={0.05}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
              <XAxis dataKey="rawEpoch" stroke="#64748b" textAnchor="middle" tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <YAxis stroke="#64748b" domain={[0, 1.0]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
              <Tooltip content={<CustomTooltip />} />
              <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase' }} />
              
              <Area type="monotone" dataKey="trainLoss" name="Training Loss" stroke="#3b82f6" strokeWidth={2} fillOpacity={1} fill="url(#trainLossGrad)" />
              <Area type="monotone" dataKey="valLoss" name="Validation Loss" stroke="#06b6d4" strokeWidth={3} fillOpacity={1} fill="url(#valLossGrad)" activeDot={{ r: 6, fill: '#06b6d4', stroke: '#fff', strokeWidth: 2 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span className="flex items-center gap-1.5 text-text-primary">
            <Activity size={14} className="text-cyan-400" /> Loss stabilzation reached with zero divergent oscillations across 20Hz stream.
          </span>
          <span className="text-cyan-400 font-bold">W&B Synchronized</span>
        </div>
      </div>

    </div>
  );
};
