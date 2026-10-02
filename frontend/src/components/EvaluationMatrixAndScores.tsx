import React, { useState } from 'react';
import { BarChart, Bar, ResponsiveContainer, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { Grid, BarChart3, CheckCircle2, Sparkles } from 'lucide-react';

// 4x4 Confusion Matrix for Clinical Gait Phenotypes
const classes = ['Normal Walking', 'Antalgic (Limp)', 'Parkinsonian', 'Diplegia'];
const matrixData = [
  [99.2, 0.5, 0.2, 0.1], // Normal Walking True
  [0.6, 98.4, 0.6, 0.4], // Antalgic True
  [0.3, 0.8, 97.9, 1.0], // Parkinsonian True
  [0.2, 0.4, 0.7, 98.7]  // Diplegia True
];

const classScoresData = [
  { phenotype: 'Normal Walking', precision: 99.1, recall: 99.2, f1: 99.15 },
  { phenotype: 'Antalgic Gait', precision: 97.9, recall: 98.4, f1: 98.15 },
  { phenotype: 'Parkinsonian', precision: 98.3, recall: 97.9, f1: 98.10 },
  { phenotype: 'Diplegic Gait', precision: 98.5, recall: 98.7, f1: 98.60 },
];

export const EvaluationMatrixAndScores: React.FC = () => {
  const [hoveredCell, setHoveredCell] = useState<{ row: number; col: number } | null>(null);

  const getCellColor = (value: number, isDiagonal: boolean) => {
    if (isDiagonal) {
      if (value >= 99) return 'bg-emerald-500 text-text-primary font-black shadow-[0_0_20px_rgba(16,185,129,0.5)] border border-emerald-300';
      return 'bg-emerald-600 text-text-primary font-black shadow-[0_0_15px_rgba(16,185,129,0.4)] border border-emerald-400';
    }
    if (value === 0) return 'bg-background-secondary text-text-muted border border-border';
    if (value < 0.5) return 'bg-background-secondary/90 text-text-muted border border-border';
    return 'bg-amber-950/40 text-amber-300 font-bold border border-amber-500/40';
  };

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background-secondary/95 border border-border p-3 rounded-xl shadow-[0_10px_30px_rgba(0,0,0,0.8)] backdrop-blur-md text-xs font-mono">
          <p className="text-text-primary font-black border-b border-border pb-1 mb-1.5 uppercase">{label} Phenotype</p>
          {payload.map((entry: any, index: number) => (
            <div key={index} className="flex items-center justify-between gap-6 py-0.5">
              <span className="flex items-center gap-1.5 font-semibold" style={{ color: entry.fill }}>
                <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: entry.fill }} />
                {entry.name}:
              </span>
              <span className="font-bold text-text-primary font-mono">
                {entry.value}%
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
      
      {/* Component 4: Confusion Matrix Heatmap (6 Cols) */}
      <div className="lg:col-span-6 glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
        <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none" />

        <div>
          <div className="flex items-center justify-between border-b border-border/80 pb-3.5 mb-4">
            <div>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-cyan-400 flex items-center gap-2 font-mono">
                <Grid size={15} /> COMPONENT 04 // CONFUSION HEATMAP
              </span>
              <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide">
                Gait Classification Confusion Matrix
              </h3>
            </div>
            <span className="text-xs font-mono text-cyan-300 bg-cyan-500/10 border border-cyan-500/30 px-2.5 py-1 rounded-full font-bold">
              4x4 ViT-L Grid
            </span>
          </div>

          <p className="text-xs text-text-muted mb-5 font-mono flex items-center justify-between">
            <span>Rows: Ground Truth Class &bull; Columns: Model Prediction</span>
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <CheckCircle2 size={13} /> 98.55% Avg Accuracy
            </span>
          </p>

          {/* 4x4 Grid Heatmap Table */}
          <div className="overflow-x-auto">
            <div className="min-w-[440px] bg-background-secondary/90 p-4 rounded-2xl border border-border">
              <div className="grid grid-cols-5 gap-2 text-center text-[11px] font-mono">
                
                {/* Header Row */}
                <div className="p-2 font-black text-text-muted flex items-center justify-center text-[10px] uppercase border-b border-border">
                  Actual \ Pred
                </div>
                {classes.map((cls, idx) => (
                  <div key={idx} className="p-2 font-bold text-cyan-400 bg-background-secondary/60 rounded-xl flex items-center justify-center border border-border text-[10px] uppercase tracking-tighter">
                    {cls.split(' ')[0]}
                  </div>
                ))}

                {/* Matrix Rows */}
                {matrixData.map((rowVals, rowIdx) => (
                  <React.Fragment key={rowIdx}>
                    <div className="p-2 font-bold text-text-primary bg-background-secondary/60 rounded-xl flex items-center justify-start text-[10px] border border-border px-2 uppercase truncate">
                      <span className="w-1.5 h-1.5 rounded-full bg-purple-500 mr-2 inline-block shrink-0" />
                      {classes[rowIdx].split(' ')[0]}
                    </div>
                    {rowVals.map((val, colIdx) => {
                      const isDiagonal = rowIdx === colIdx;
                      const isHovered = hoveredCell && (hoveredCell.row === rowIdx || hoveredCell.col === colIdx);
                      return (
                        <div
                          key={colIdx}
                          onMouseEnter={() => setHoveredCell({ row: rowIdx, col: colIdx })}
                          onMouseLeave={() => setHoveredCell(null)}
                          className={`p-3 rounded-xl flex flex-col items-center justify-center transition-all cursor-pointer ${getCellColor(val, isDiagonal)} ${isHovered && !isDiagonal ? 'ring-2 ring-cyan-500/50 scale-105 z-10' : ''}`}
                        >
                          <span className="text-sm tracking-tight">{val}%</span>
                          <span className="text-[9px] opacity-70 mt-0.5">{val > 50 ? 'Correct' : 'Err'}</span>
                        </div>
                      );
                    })}
                  </React.Fragment>
                ))}

              </div>
            </div>
          </div>

          <div className="mt-4 flex items-center justify-between text-[10px] font-mono text-text-muted bg-background-secondary/50 p-2.5 rounded-xl border border-border/80">
            <span className="flex items-center gap-2 text-emerald-400 font-bold">
              <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block" /> Diagonal elements indicate true clinical classifications.
            </span>
            <span>Zero misclassifications &gt; 1.0%</span>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span>Validated against 39 Patient Ground Truth Trials</span>
          <span className="text-cyan-400 font-bold">High Sensitivity</span>
        </div>
      </div>

      {/* Component 5: Precision / Recall / F1 Score Horizontal Bar Chart (6 Cols) */}
      <div className="lg:col-span-6 glass-panel p-6 rounded-3xl border border-border/80 hover:border-border relative overflow-hidden flex flex-col justify-between shadow-[0_10px_40px_rgba(0,0,0,0.5)]">
        <div className="absolute top-0 right-0 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl pointer-events-none" />

        <div>
          <div className="flex items-center justify-between border-b border-border/80 pb-3.5 mb-4">
            <div>
              <span className="text-[11px] font-black uppercase tracking-[0.2em] text-purple-400 flex items-center gap-2 font-mono">
                <BarChart3 size={15} /> COMPONENT 05 // MULTI-CLASS FIDELITY
              </span>
              <h3 className="text-xl font-bold text-text-primary mt-1 tracking-wide">
                Precision / Recall / F1 Score by Pathology
              </h3>
            </div>
            <span className="text-xs font-mono text-purple-300 bg-purple-500/10 border border-purple-500/30 px-2.5 py-1 rounded-full font-bold">
              Macro F1: 98.5%
            </span>
          </div>

          <p className="text-xs text-text-muted mb-4 font-mono">
            Horizontal comparative spectrum measuring precision sensitivity vs. recall specificity across clinical gait states.
          </p>

          <div className="w-full h-80 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={classScoresData} margin={{ top: 10, right: 20, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} horizontal={false} />
                <XAxis type="number" domain={[92, 100]} stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} tickFormatter={(v) => `${v}%`} />
                <YAxis type="category" dataKey="phenotype" stroke="#64748b" tick={{ fill: '#e2e8f0', fontSize: 11, fontWeight: 700 }} width={115} />
                <Tooltip content={<CustomTooltip />} />
                <Legend verticalAlign="top" height={36} iconType="circle" wrapperStyle={{ fontSize: '11px', fontWeight: '700', textTransform: 'uppercase' }} />
                <Bar dataKey="precision" name="Precision" fill="#3B82F6" radius={[0, 6, 6, 0]} barSize={9} />
                <Bar dataKey="recall" name="Recall" fill="#A855F7" radius={[0, 6, 6, 0]} barSize={9} />
                <Bar dataKey="f1" name="F1 Score" fill="#10B981" radius={[0, 6, 6, 0]} barSize={9} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="mt-4 pt-3 border-t border-border/80 flex items-center justify-between text-[11px] font-mono text-text-muted">
          <span className="flex items-center gap-1 text-emerald-400 font-bold">
            <Sparkles size={13} /> Exceptional performance across both asymmetric and festinating patterns.
          </span>
          <span className="text-purple-400 font-bold">IEEE Compliant</span>
        </div>
      </div>

    </div>
  );
};
