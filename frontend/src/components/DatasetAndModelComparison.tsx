import React from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { PieChart as PieIcon, Zap, Trophy } from 'lucide-react';

const datasetDistribution = [
  { name: 'Normal Gait Samples', value: 842000, color: '#10B981' },
  { name: 'Abnormal Pathology Samples', value: 578000, color: '#F59E0B' }
];

const partitionStats = [
  { label: 'Training Partition', count: '1,420,000 frames', percentage: '73.2%', bg: 'bg-purple-500/10 text-purple-300 border-purple-500/30' },
  { label: 'Validation Partition', count: '340,000 frames', percentage: '17.5%', bg: 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30' },
  { label: 'Test Partition (Sealed)', count: '185,000 frames', percentage: '9.3%', bg: 'bg-emerald-500/10 text-emerald-300 border-emerald-500/30' }
];

const modelComparisonData = [
  { model: 'CNN (Baseline)', accuracy: 91.4, precision: 90.2, recall: 91.0, f1: 90.6, inferenceTime: 3.2, params: '4.2M', status: 'Legacy' },
  { model: 'ResNet-50', accuracy: 94.8, precision: 94.1, recall: 95.0, f1: 94.5, inferenceTime: 12.6, params: '25.6M', status: 'Standard' },
  { model: 'EfficientNet-B4', accuracy: 96.2, precision: 95.8, recall: 96.5, f1: 96.1, inferenceTime: 9.4, params: '19.3M', status: 'Competitive' },
  { model: 'Vision Transformer (ViT)', accuracy: 98.6, precision: 98.1, recall: 98.7, f1: 98.4, inferenceTime: 8.4, params: '32.1M', status: 'SOTA Peak' }
];

export const DatasetAndModelComparison: React.FC = () => {

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background-secondary/95 border border-border p-3 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)] backdrop-blur-md text-xs font-mono">
          <p className="text-text-primary font-black border-b border-border pb-1 mb-1.5">{label || payload[0]?.name}</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-6 py-0.5">
              <span className="flex items-center gap-1.5 font-semibold" style={{ color: entry.color || entry.fill }}>
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: entry.color || entry.fill }} />
                {entry.name}:
              </span>
              <span className="font-bold text-text-primary font-mono">
                {entry.value.toLocaleString()}{entry.unit || (typeof entry.value === 'number' && entry.value <= 100 ? '%' : '')}
              </span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 w-full">
      
      {/* Component 3: Dataset Distribution (5 Cols) */}
      <div className="lg:col-span-5 glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
        <div className="absolute top-0 left-0 w-40 h-40 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />

        <div>
          <div className="flex items-center justify-between border-b border-border/80 pb-3.5 mb-4">
            <div>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-emerald-400 flex items-center gap-2 font-mono">
                <PieIcon size={15} /> COMPONENT 03 // LINEAGE COMPOSITION
              </span>
              <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide">
                Dataset Distribution & Partitions
              </h3>
            </div>
            <span className="text-xs font-mono text-emerald-300 bg-emerald-500/10 border border-emerald-500/30 px-2.5 py-1 rounded-full font-bold">
              1.94M Total
            </span>
          </div>

          <div className="h-56 flex items-center justify-center relative">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={datasetDistribution}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, percent }: any) => `${(name || '').split(' ')[0]}: ${((percent || 0) * 100).toFixed(1)}%`}
                  labelLine={false}
                >
                  {datasetDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="#020617" strokeWidth={3} />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>

            {/* Inner center text */}
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-center pointer-events-none">
              <span className="text-xs font-mono text-text-muted block uppercase">Balance</span>
              <span className="text-lg font-black text-text-primary font-mono">59 / 41</span>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 mb-4">
            <div className="p-3 rounded-2xl bg-background-secondary/80 border border-emerald-500/20 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-text-muted font-mono block uppercase">Normal Samples</span>
                <span className="text-base font-black text-emerald-400 font-mono">842,000</span>
              </div>
              <span className="w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.5)]" />
            </div>
            <div className="p-3 rounded-2xl bg-background-secondary/80 border border-amber-500/20 flex items-center justify-between">
              <div>
                <span className="text-[10px] text-text-muted font-mono block uppercase">Abnormal Pathology</span>
                <span className="text-base font-black text-amber-400 font-mono">578,000</span>
              </div>
              <span className="w-3 h-3 rounded-full bg-amber-500 shadow-[0_0_8px_rgba(245,158,11,0.5)]" />
            </div>
          </div>

          <div className="space-y-2">
            <span className="text-[11px] font-black uppercase text-text-muted tracking-wider font-mono block">
              PARTITION BREAKDOWN (TRAIN / VAL / TEST)
            </span>
            {partitionStats.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-2.5 rounded-xl bg-background-secondary/60 border border-border text-xs font-mono">
                <span className="text-text-primary font-bold flex items-center gap-2">
                  <span className={`px-2 py-0.5 rounded text-[10px] font-black ${item.bg}`}>{item.percentage}</span>
                  {item.label}
                </span>
                <span className="text-text-primary font-mono font-black">{item.count}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span>Sealed against data leakage</span>
          <span className="text-emerald-400 font-bold">Hash Verified</span>
        </div>
      </div>

      {/* Component 6: Model Comparison Suite (7 Cols) */}
      <div className="lg:col-span-7 glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
        <div className="absolute top-0 right-0 w-48 h-48 bg-purple-600/10 rounded-full blur-3xl pointer-events-none" />

        <div>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-border/80 pb-3.5 mb-4">
            <div>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-purple-400 flex items-center gap-2 font-mono">
                <Trophy size={15} /> COMPONENT 06 // ARCHITECTURAL BENCHMARK SUITE
              </span>
              <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide flex items-center gap-2">
                Deep Learning Model Comparison
              </h3>
            </div>
            <span className="text-xs font-mono text-purple-300 bg-purple-500/10 border border-purple-500/30 px-3 py-1 rounded-full font-bold flex items-center gap-1.5">
              <Zap size={13} className="text-amber-400" /> SOTA: ViT-Gait3D (8.4ms)
            </span>
          </div>

          <p className="text-xs text-text-muted mb-4 font-mono">
            Evaluating Accuracy, Precision, Recall, and F1 Score against real-time Edge Wi-Fi Inference Time.
          </p>

          {/* Grouped Bar Chart */}
          <div className="w-full h-56 pt-2 mb-6">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={modelComparisonData} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} />
                <XAxis dataKey="model" stroke="#64748b" tick={{ fill: '#e2e8f0', fontSize: 11, fontWeight: 600 }} />
                <YAxis stroke="#64748b" domain={[80, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(val) => `${val}%`} />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" height={32} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase' }} />
                <Bar dataKey="accuracy" name="Accuracy" fill="#10B981" radius={[4, 4, 0, 0]} />
                <Bar dataKey="precision" name="Precision" fill="#3B82F6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="recall" name="Recall" fill="#A855F7" radius={[4, 4, 0, 0]} />
                <Bar dataKey="f1" name="F1 Score" fill="#F59E0B" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Comparative Metrics Table */}
          <div className="overflow-x-auto rounded-2xl border border-border bg-background-secondary/80">
            <table className="w-full text-left font-mono text-xs">
              <thead className="bg-background-secondary/90 text-text-muted text-[11px] uppercase tracking-wider border-b border-border">
                <tr>
                  <th className="py-3 px-4 font-black">Model Architecture</th>
                  <th className="py-3 px-2 text-center">Accuracy</th>
                  <th className="py-3 px-2 text-center">Precision</th>
                  <th className="py-3 px-2 text-center">Recall</th>
                  <th className="py-3 px-2 text-center">F1 Score</th>
                  <th className="py-3 px-3 text-right font-black text-cyan-400">Inference Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-text-primary">
                {modelComparisonData.map((row, index) => (
                  <tr key={index} className={`hover:bg-purple-500/10 transition-colors ${row.model.includes('ViT') ? 'bg-purple-950/25 font-bold text-text-primary' : ''}`}>
                    <td className="py-3 px-4 flex items-center gap-2">
                      <span className={`w-2 h-2 rounded-full ${row.model.includes('ViT') ? 'bg-purple-400 animate-ping' : 'bg-card-hover'}`} />
                      <span>{row.model}</span>
                      {row.model.includes('ViT') && (
                        <span className="ml-1 text-[9px] bg-purple-500 text-text-primary px-2 py-0.5 rounded-md font-sans uppercase font-black shadow-[0_0_10px_rgba(168,85,247,0.5)]">Ours</span>
                      )}
                    </td>
                    <td className="py-3 px-2 text-center font-black text-emerald-400">{row.accuracy}%</td>
                    <td className="py-3 px-2 text-center text-blue-400">{row.precision}%</td>
                    <td className="py-3 px-2 text-center text-purple-400">{row.recall}%</td>
                    <td className="py-3 px-2 text-center font-bold text-amber-400">{row.f1}%</td>
                    <td className="py-3 px-3 text-right font-black text-cyan-300 bg-cyan-500/5">{row.inferenceTime} ms</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span>Benchmarked on Netgear WAN/LAN RSSI 20Hz Packet Feed</span>
          <span className="text-purple-400 font-bold">Hugging Face Hub Validated</span>
        </div>
      </div>

    </div>
  );
};
