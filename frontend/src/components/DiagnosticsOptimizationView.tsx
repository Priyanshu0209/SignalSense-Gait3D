import React, { useState } from 'react';
import { Wrench, CheckCircle, AlertTriangle, Info, Download } from 'lucide-react';

export const DiagnosticsOptimizationView: React.FC<{ opsState: any }> = ({ opsState }) => {
  const { diagnostics, generateReport } = opsState;
  const [isGenerating, setIsGenerating] = useState(false);

  if (!diagnostics) return null;

  const handleGenerate = async () => {
    setIsGenerating(true);
    const res = await generateReport();
    if (res?.file) alert(`Report generated at: ${res.file}`);
    setIsGenerating(false);
  };

  return (
    <div className="space-y-6">
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-2">
            <Wrench className="text-teal-500" /> Diagnostics & Optimization
          </h2>
          <p className="text-text-muted text-sm">Automated system scans, integrity checks, and cleanup recommendations.</p>
        </div>
        <button onClick={handleGenerate} disabled={isGenerating} className="flex items-center gap-2 bg-card hover:bg-card-hover text-text-primary px-4 py-2 rounded-lg text-sm font-bold transition-colors">
          <Download size={16} /> {isGenerating ? 'GENERATING...' : 'EXPORT OPS REPORT'}
        </button>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase">System Integrity Scan</h3>
            <span className={`px-2 py-1 rounded text-[10px] font-bold tracking-wider uppercase ${
              diagnostics.status === 'Healthy' ? 'bg-green-500/10 text-green-400 border border-green-500/20' : 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20'
            }`}>
              {diagnostics.status}
            </span>
          </div>

          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-card p-4 rounded-lg">
              <p className="text-2xl font-light text-text-primary">{diagnostics.datasets_scanned}</p>
              <p className="text-xs font-bold text-text-muted">DATASETS SCANNED</p>
            </div>
            <div className="bg-card p-4 rounded-lg">
              <p className="text-2xl font-light text-text-primary">{diagnostics.models_scanned}</p>
              <p className="text-xs font-bold text-text-muted">MODELS SCANNED</p>
            </div>
          </div>

          <div className="space-y-3">
            {diagnostics.issues_found.length === 0 ? (
              <div className="flex items-center gap-3 text-green-400 bg-green-500/5 p-4 rounded border border-green-500/20">
                <CheckCircle size={20} />
                <span className="text-sm font-bold">No integrity issues found.</span>
              </div>
            ) : (
              diagnostics.issues_found.map((issue: any, idx: number) => (
                <div key={idx} className="flex items-start gap-3 text-yellow-400 bg-yellow-500/5 p-4 rounded border border-yellow-500/20">
                  <AlertTriangle size={20} className="mt-0.5 shrink-0" />
                  <div>
                    <span className="text-sm font-bold block">{issue.type} Issue</span>
                    <span className="text-xs text-yellow-500/80">{issue.message}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-6">Optimization Recommendations</h3>
          <div className="space-y-3">
            {diagnostics.recommendations.map((rec: string, idx: number) => (
              <div key={idx} className="flex items-center gap-3 text-blue-400 bg-blue-500/5 p-4 rounded border border-blue-500/20">
                <Info size={20} className="shrink-0" />
                <span className="text-sm font-medium text-text-primary">{rec}</span>
              </div>
            ))}
            {diagnostics.recommendations.length === 0 && (
              <p className="text-text-muted italic text-sm">System is fully optimized.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
