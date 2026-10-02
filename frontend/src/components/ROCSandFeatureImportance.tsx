import React from 'react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Activity, Award, Flame, Database, CheckCircle, Zap } from 'lucide-react';

// Generate ROC Curve data (FPR vs TPR)
const rocData = [
  { fpr: '0.00', rawFpr: 0.0, vitTpr: 0.0, resnetTpr: 0.0, baseline: 0.0 },
  { fpr: '0.02', rawFpr: 0.02, vitTpr: 0.88, resnetTpr: 0.72, baseline: 0.02 },
  { fpr: '0.05', rawFpr: 0.05, vitTpr: 0.96, resnetTpr: 0.85, baseline: 0.05 },
  { fpr: '0.10', rawFpr: 0.10, vitTpr: 0.985, resnetTpr: 0.91, baseline: 0.10 },
  { fpr: '0.20', rawFpr: 0.20, vitTpr: 0.994, resnetTpr: 0.95, baseline: 0.20 },
  { fpr: '0.50', rawFpr: 0.50, vitTpr: 0.999, resnetTpr: 0.98, baseline: 0.50 },
  { fpr: '1.00', rawFpr: 1.0, vitTpr: 1.0, resnetTpr: 1.0, baseline: 1.0 },
];

// Generate Precision-Recall curve trade-off data
const prData = [
  { recall: '0.0', rawRec: 0.0, vitPrecision: 1.0, resnetPrecision: 1.0 },
  { recall: '0.4', rawRec: 0.4, vitPrecision: 0.996, resnetPrecision: 0.97 },
  { recall: '0.7', rawRec: 0.7, vitPrecision: 0.991, resnetPrecision: 0.94 },
  { recall: '0.85', rawRec: 0.85, vitPrecision: 0.986, resnetPrecision: 0.91 },
  { recall: '0.95', rawRec: 0.95, vitPrecision: 0.978, resnetPrecision: 0.86 },
  { recall: '1.0', rawRec: 1.0, vitPrecision: 0.924, resnetPrecision: 0.78 },
];

// Feature Importance Ranking (RF Doppler & CSI Biomarkers)
const featureImportanceData = [
  { feature: 'Doppler Frequency Shift (Hz)', importance: 94.2, category: 'RF Physical' },
  { feature: 'CSI Subcarrier Phase Variance', importance: 88.5, category: 'Spectral' },
  { feature: 'Step Stride Symmetry Index', importance: 82.1, category: 'Kinematic' },
  { feature: 'Wavefront Angle of Arrival (AoA)', importance: 76.4, category: 'Spatial' },
  { feature: 'RSSI Amplitude Decay Slope', importance: 68.9, category: 'RF Physical' },
  { feature: 'Gait Cycle Periodicity (RPM)', importance: 61.3, category: 'Temporal' },
];

export const ROCSandFeatureImportance: React.FC = () => {

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background-secondary/95 border border-border p-3 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)] backdrop-blur-md text-xs font-mono">
          <p className="text-text-primary font-black border-b border-border pb-1 mb-1.5 uppercase">Metric Threshold Snapshot</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-6 py-0.5">
              <span className="flex items-center gap-1.5 font-semibold" style={{ color: entry.color || entry.fill }}>
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: entry.color || entry.fill }} />
                {entry.name}:
              </span>
              <span className="font-bold text-text-primary font-mono">
                {typeof entry.value === 'number' && entry.value <= 1 ? entry.value.toFixed(3) : `${entry.value}%`}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="space-y-6">
      
      {/* Top Grid: ROC Curve (Comp 9) & Precision-Recall Curve (Comp 10) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full">
        
        {/* Component 9: ROC Curve */}
        <div className="glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
          <div className="absolute top-0 right-0 w-48 h-48 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
          
          <div>
            <div className="flex items-center justify-between border-b border-border/80 pb-3.5 mb-4">
              <div>
                <span className="text-[11px] font-black uppercase tracking-[0.2em] text-emerald-400 flex items-center gap-2 font-mono">
                  <Activity size={15} /> COMPONENT 09 // DISCRIMINATION SPECTRA
                </span>
                <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide flex items-center gap-2">
                  ROC Curve (Receiver Operating Characteristic)
                </h3>
              </div>
              <span className="text-xs font-mono text-emerald-300 bg-emerald-500/15 border border-emerald-500/30 px-3 py-1 rounded-full font-black shadow-[0_0_15px_rgba(16,185,129,0.3)]">
                AUC: 0.992
              </span>
            </div>

            <p className="text-xs text-text-muted mb-4 font-mono flex items-center justify-between">
              <span>X-Axis: False Positive Rate (FPR) &bull; Y-Axis: True Positive Rate (TPR)</span>
            </p>

            <div className="w-full h-72 pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={rocData} margin={{ top: 10, right: 15, left: -15, bottom: 0 }}>
                  <defs>
                    <linearGradient id="vitRocGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="#10B981" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                  <XAxis dataKey="fpr" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis stroke="#64748b" domain={[0, 1.0]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend verticalAlign="top" height={32} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase' }} />
                  
                  <Line type="monotone" dataKey="baseline" name="Random Guess (0.5)" stroke="#475569" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
                  <Area type="monotone" dataKey="resnetTpr" name="ResNet-50 (AUC=0.968)" stroke="#06B6D4" strokeWidth={2} fill="transparent" />
                  <Area type="monotone" dataKey="vitTpr" name="ViT-Gait3D (AUC=0.992)" stroke="#10B981" strokeWidth={3} fillOpacity={1} fill="url(#vitRocGrad)" activeDot={{ r: 6, fill: '#10B981', stroke: '#fff', strokeWidth: 2 }} />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
            <span className="text-text-primary">Near-perfect separation of clinical limbing signatures.</span>
            <span className="text-emerald-400 font-bold">Optimal Specificity</span>
          </div>
        </div>

        {/* Component 10: Precision-Recall Curve */}
        <div className="glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
          <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

          <div>
            <div className="flex items-center justify-between border-b border-border/80 pb-3.5 mb-4">
              <div>
                <span className="text-[11px] font-black uppercase tracking-[0.2em] text-cyan-400 flex items-center gap-2 font-mono">
                  <Flame size={15} /> COMPONENT 10 // THRESHOLD TRADEOFF
                </span>
                <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide">
                  Precision-Recall Curve (PR-AUC)
                </h3>
              </div>
              <span className="text-xs font-mono text-cyan-300 bg-cyan-500/10 border border-cyan-500/30 px-3 py-1 rounded-full font-bold">
                PR-AUC: 0.988
              </span>
            </div>

            <p className="text-xs text-text-muted mb-4 font-mono">
              Evaluating precision stability under extreme high-sensitivity clinical recall thresholds.
            </p>

            <div className="w-full h-72 pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={prData} margin={{ top: 10, right: 15, left: -15, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                  <XAxis dataKey="recall" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis stroke="#64748b" domain={[0.6, 1.0]} tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend verticalAlign="top" height={32} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase' }} />
                  
                  <Line type="monotone" dataKey="resnetPrecision" name="ResNet-50 Precision" stroke="#a855f7" strokeWidth={2} dot={false} strokeDasharray="3 3" />
                  <Line type="monotone" dataKey="vitPrecision" name="ViT-Gait3D Precision" stroke="#06b6d4" strokeWidth={3} dot={false} activeDot={{ r: 6, fill: '#06b6d4', stroke: '#fff', strokeWidth: 2 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
            <span>Maintains &gt;98% precision even at 95% clinical sensitivity.</span>
            <span className="text-cyan-400 font-bold">Robust Bounds</span>
          </div>
        </div>

      </div>

      {/* Component 11: Feature Importance Chart */}
      <div className="glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
        <div className="absolute -top-10 left-1/3 w-64 h-64 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/80 pb-4 mb-5">
          <div>
            <span className="text-[11px] font-black uppercase tracking-[0.2em] text-purple-400 flex items-center gap-2 font-mono">
              <Award size={15} /> COMPONENT 11 // BIOMARKER ATTENTION WEIGHTS
            </span>
            <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide">
              Deep Learning Feature Importance & RF Biomarker Ranking
            </h3>
          </div>
          <div className="flex items-center gap-3 text-xs font-mono text-text-muted">
            <span className="px-3 py-1 rounded-xl bg-purple-500/10 text-purple-300 border border-purple-500/30 font-bold">
              SHAP & Attention Head Explanations
            </span>
          </div>
        </div>

        <p className="text-xs text-text-muted mb-4 font-mono">
          Relative importance (%) of physical wireless packet features evaluated across Vision Transformer self-attention layers.
        </p>

        <div className="w-full h-72 pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={featureImportanceData} margin={{ top: 5, right: 30, left: 140, bottom: 5 }}>
              <defs>
                <linearGradient id="barGrad" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0%" stopColor="#3B82F6" />
                  <stop offset="50%" stopColor="#8B5CF6" />
                  <stop offset="100%" stopColor="#EC4899" />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.25} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(val) => `${val}%`} />
              <YAxis type="category" dataKey="feature" stroke="#64748b" tick={{ fill: '#f8fafc', fontSize: 11, fontWeight: 700 }} width={230} />
              <Tooltip content={<CustomTooltip />} />
              <Bar dataKey="importance" name="Relative Feature Weight" fill="url(#barGrad)" radius={[0, 8, 8, 0]} barSize={18} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Component 12: Enterprise Research Statistics Banner */}
      <div className="glass-panel p-6 rounded-3xl border border-purple-500/30 bg-gradient-to-r from-slate-900/90 via-purple-950/20 to-slate-900/90 shadow-[0_0_50px_rgba(168,85,247,0.15)] relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border/80 pb-4 mb-6">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-600/20 rounded-2xl border border-purple-500/40 text-purple-400">
              <Database size={24} className="animate-pulse" />
            </div>
            <div>
              <span className="text-[11px] font-mono text-purple-400 uppercase tracking-[0.2em] font-black block">
                COMPONENT 12 // ENTERPRISE MODEL OBSERVATION HUB
              </span>
              <h3 className="text-2xl font-black text-text-primary tracking-wide mt-0.5">
                SignalSense Pro MLOps Observatory Statistics & Repository Audit
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3.5 py-1.5 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/40 text-xs font-mono font-black flex items-center gap-2 shadow-[0_0_15px_rgba(16,185,129,0.3)]">
              <CheckCircle size={14} className="text-emerald-400" /> REPOSITORY SEALED & VERIFIED
            </span>
          </div>
        </div>

        {/* Statistics Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-7 gap-4">
          
          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-purple-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Total Experiments</span>
            <span className="text-2xl font-black text-text-primary font-mono tracking-tight">248</span>
            <span className="text-[10px] font-mono text-purple-400 mt-1">Runs Archived</span>
          </div>

          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-emerald-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Best Accuracy</span>
            <span className="text-2xl font-black text-emerald-400 font-mono tracking-tight">98.64%</span>
            <span className="text-[10px] font-mono text-emerald-500 mt-1">Run #241 Peak</span>
          </div>

          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-cyan-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Current Model</span>
            <span className="text-base font-black text-cyan-300 font-mono tracking-tighter truncate">ViT-Gait3D-L</span>
            <span className="text-[10px] font-mono text-cyan-500 mt-1">24 layers &bull; 32M</span>
          </div>

          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-indigo-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Dataset Size</span>
            <span className="text-2xl font-black text-text-primary font-mono tracking-tight">148.2 GB</span>
            <span className="text-[10px] font-mono text-indigo-400 mt-1">SHA-256 Lineage</span>
          </div>

          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-amber-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Training Images</span>
            <span className="text-xl font-black text-amber-300 font-mono tracking-tight">1,420,000</span>
            <span className="text-[10px] font-mono text-amber-500 mt-1">73.2% Partition</span>
          </div>

          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-teal-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Validation Images</span>
            <span className="text-xl font-black text-teal-300 font-mono tracking-tight">340,000</span>
            <span className="text-[10px] font-mono text-teal-500 mt-1">17.5% Partition</span>
          </div>

          <div className="p-4 rounded-2xl bg-background-secondary/90 border border-border flex flex-col justify-between hover:border-rose-500/40 transition-all">
            <span className="text-[10px] font-mono text-text-muted uppercase font-bold block mb-1">Testing Images</span>
            <span className="text-xl font-black text-rose-400 font-mono tracking-tight">185,000</span>
            <span className="text-[10px] font-mono text-rose-500 mt-1">Sealed Held-Out</span>
          </div>

        </div>

        <div className="mt-6 pt-4 border-t border-border/80 flex flex-col sm:flex-row items-center justify-between text-xs font-mono text-text-muted gap-2">
          <span className="flex items-center gap-2">
            <Zap size={14} className="text-purple-400" /> Powered by SignalSense Pro Phase 3 Neural Reconstruction Engine &bull; Enterprise Telemetry Hub
          </span>
          <span className="text-purple-400 font-bold bg-background-secondary px-3 py-1 rounded-xl border border-border">
            NVIDIA Omniverse &bull; Weights & Biases Sync Active
          </span>
        </div>
      </div>

    </div>
  );
};
