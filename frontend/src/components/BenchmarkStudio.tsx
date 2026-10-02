import React, { useState } from 'react';
import { Play, Download, BarChart2 } from 'lucide-react';

export const BenchmarkStudio: React.FC<{ locState: any, aiState: any }> = ({ locState, aiState }) => {
  const { runBenchmark, generateReport } = locState;
  const { datasets, models } = aiState;

  const [selectedDataset, setSelectedDataset] = useState('');
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [isBenchmarking, setIsBenchmarking] = useState(false);
  const [benchmarkResults, setBenchmarkResults] = useState<any>(null);

  const handleRun = async () => {
    if (!selectedDataset || selectedModels.length === 0) return;
    setIsBenchmarking(true);
    try {
      const res = await runBenchmark(selectedDataset, selectedModels);
      setBenchmarkResults(res);
    } catch (e) {
      console.error(e);
    }
    setIsBenchmarking(false);
  };

  const handleGenerateReport = async () => {
    if (!benchmarkResults) return;
    try {
      const res = await generateReport(benchmarkResults);
      alert(`Report generated: ${res.file}`);
    } catch (e) {
      console.error(e);
    }
  };

  const toggleModel = (id: string) => {
    if (selectedModels.includes(id)) {
      setSelectedModels(selectedModels.filter(m => m !== id));
    } else {
      setSelectedModels([...selectedModels, id]);
    }
  };

  return (
    <div className="flex-1 flex flex-col gap-6">
      <div className="grid grid-cols-12 gap-6 h-full">
        {/* Configuration Panel */}
        <div className="col-span-4 glass-panel p-6 flex flex-col gap-6 h-full">
          <div>
            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase">1. Select Dataset</h3>
            <select 
              value={selectedDataset} 
              onChange={e => setSelectedDataset(e.target.value)}
              className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500"
            >
              <option value="">Select a Dataset...</option>
              {datasets.map((d: any) => <option key={d.filename} value={d.filename}>{d.name || d.filename}</option>)}
            </select>
          </div>

          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase">2. Select Models ({selectedModels.length})</h3>
            <div className="space-y-2">
              {models.map((m: any) => (
                <div 
                  key={m.id} 
                  onClick={() => toggleModel(m.id)}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedModels.includes(m.id) 
                      ? 'bg-blue-600/20 border-blue-500/50 text-text-primary' 
                      : 'bg-card border-border text-text-muted hover:border-border'
                  }`}
                >
                  <p className="font-bold text-sm">{m.name}</p>
                  <p className="text-xs font-mono opacity-70">{m.algorithm} | Base Acc: {m.accuracy}%</p>
                </div>
              ))}
              {models.length === 0 && <p className="text-text-muted italic text-sm">No models available in registry.</p>}
            </div>
          </div>

          <button 
            onClick={handleRun}
            disabled={!selectedDataset || selectedModels.length === 0 || isBenchmarking}
            className={`w-full flex items-center justify-center gap-2 py-3 rounded-lg font-bold transition-all ${
              !selectedDataset || selectedModels.length === 0
                ? 'bg-card text-text-muted cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-500 text-text-primary shadow-[0_0_15px_rgba(37,99,235,0.4)]'
            }`}
          >
            {isBenchmarking ? <BarChart2 className="animate-spin" size={18} /> : <Play size={18} />}
            {isBenchmarking ? 'RUNNING BENCHMARK...' : 'RUN BENCHMARK'}
          </button>
        </div>

        {/* Results Panel */}
        <div className="col-span-8 glass-panel p-6 overflow-hidden flex flex-col">
          <div className="flex justify-between items-center mb-6">
            <h3 className="text-sm font-bold tracking-wider text-text-muted uppercase">Benchmark Results</h3>
            {benchmarkResults && (
              <button onClick={handleGenerateReport} className="flex items-center gap-2 bg-card hover:bg-card-hover text-text-primary px-4 py-2 rounded-lg text-sm font-bold transition-colors">
                <Download size={16} /> GENERATE REPORT
              </button>
            )}
          </div>
          
          {!benchmarkResults ? (
            <div className="flex-1 flex flex-col items-center justify-center text-text-muted opacity-50">
              <BarChart2 size={64} className="mb-4" />
              <p className="font-mono tracking-widest text-sm">AWAITING BENCHMARK EXECUTION</p>
            </div>
          ) : (
            <div className="flex-1 overflow-auto custom-scrollbar">
              <div className="mb-6 bg-card p-4 rounded-xl border border-border flex gap-8">
                <div>
                  <p className="text-xs font-bold text-text-muted mb-1">DATASET EVALUATED</p>
                  <p className="font-mono text-text-primary text-sm">{benchmarkResults.dataset}</p>
                </div>
                <div>
                  <p className="text-xs font-bold text-text-muted mb-1">TOTAL SAMPLES</p>
                  <p className="font-mono text-text-primary text-sm">{benchmarkResults.samples}</p>
                </div>
              </div>
              
              <table className="w-full text-left text-sm text-text-primary">
                <thead className="bg-card text-text-muted text-xs uppercase tracking-wider">
                  <tr>
                    <th className="px-6 py-4">Model Name</th>
                    <th className="px-6 py-4">Algorithm</th>
                    <th className="px-6 py-4">MAE (m)</th>
                    <th className="px-6 py-4">RMSE (m)</th>
                    <th className="px-6 py-4 text-right">Inference Speed</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-foreground/5">
                  {[...benchmarkResults.results].sort((a, b) => a.mae - b.mae).map((res: any, idx: number) => (
                    <tr key={res.model_name} className={`${idx === 0 ? 'bg-green-500/10' : 'hover:bg-foreground/5'}`}>
                      <td className="px-6 py-4 font-medium text-text-primary flex items-center gap-2">
                        {idx === 0 && <span className="bg-green-500 text-black text-[10px] font-bold px-1.5 py-0.5 rounded">BEST</span>}
                        {res.model_name}
                      </td>
                      <td className="px-6 py-4 font-mono text-xs">{res.algorithm}</td>
                      <td className={`px-6 py-4 font-mono font-bold ${idx === 0 ? 'text-green-400' : 'text-text-primary'}`}>{res.mae}</td>
                      <td className={`px-6 py-4 font-mono ${idx === 0 ? 'text-green-400' : 'text-text-primary'}`}>{res.rmse}</td>
                      <td className="px-6 py-4 text-right font-mono text-text-muted">{res.inference_time_ms.toFixed(1)} ms</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
