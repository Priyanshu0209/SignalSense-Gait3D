import React, { useState } from 'react';
import { Play, Square, Activity, Cpu, Database, Settings2 } from 'lucide-react';

export const ModelTrainingView: React.FC<{ aiState: any }> = ({ aiState }) => {
  const [config, setConfig] = useState({
    dataset: '',
    algorithm: 'Random Forest',
    epochs: 50,
    learning_rate: 0.01,
    max_depth: 10,
    split_train: 70,
    split_val: 15,
    split_test: 15
  });

  const { datasets, trainingProgress, startTraining, stopTraining } = aiState;
  const isTraining = trainingProgress !== null;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider">Model Training Engine</h2>
          <p className="text-text-muted text-sm">Configure hyperparameters and train ML models in the background.</p>
        </div>
        {isTraining ? (
          <button onClick={stopTraining} className="btn-danger flex items-center gap-2 bg-red-600/20 hover:bg-red-600/40 text-red-500 border border-red-500/50 px-6 py-2 rounded-lg font-bold shadow-[0_0_15px_rgba(220,38,38,0.3)]">
            <Square size={18} /> STOP TRAINING
          </button>
        ) : (
          <button onClick={() => startTraining(config)} className="btn-primary flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-text-primary px-6 py-2 rounded-lg font-bold shadow-[0_0_15px_rgba(37,99,235,0.4)]">
            <Play size={18} /> START TRAINING
          </button>
        )}
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Configuration Panel */}
        <div className="col-span-12 xl:col-span-4 space-y-6">
          <div className="glass-panel p-6 opacity-100 transition-opacity" style={{ opacity: isTraining ? 0.5 : 1 }}>
            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase flex items-center gap-2">
              <Database size={16} /> Dataset Selection
            </h3>
            <select 
              value={config.dataset} 
              onChange={e => setConfig({...config, dataset: e.target.value})}
              disabled={isTraining}
              className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500 mb-4"
            >
              <option value="">Select a Dataset...</option>
              {datasets.map((d: any) => <option key={d.filename} value={d.filename}>{d.name || d.filename}</option>)}
            </select>

            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 mt-6 uppercase flex items-center gap-2">
              <Settings2 size={16} /> Data Split (%)
            </h3>
            <div className="grid grid-cols-3 gap-2">
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1 text-center">Train</label>
                <input type="number" value={config.split_train} onChange={e => setConfig({...config, split_train: parseInt(e.target.value)||0})} disabled={isTraining} className="w-full bg-card border border-border rounded-lg p-2 text-sm text-text-primary text-center focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1 text-center">Val</label>
                <input type="number" value={config.split_val} onChange={e => setConfig({...config, split_val: parseInt(e.target.value)||0})} disabled={isTraining} className="w-full bg-card border border-border rounded-lg p-2 text-sm text-text-primary text-center focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1 text-center">Test</label>
                <input type="number" value={config.split_test} onChange={e => setConfig({...config, split_test: parseInt(e.target.value)||0})} disabled={isTraining} className="w-full bg-card border border-border rounded-lg p-2 text-sm text-text-primary text-center focus:outline-none focus:border-blue-500" />
              </div>
            </div>

            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 mt-6 uppercase flex items-center gap-2">
              <Cpu size={16} /> Hyperparameters
            </h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1">Algorithm</label>
                <select value={config.algorithm} onChange={e => setConfig({...config, algorithm: e.target.value})} disabled={isTraining} className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500">
                  <option>Random Forest</option>
                  <option>XGBoost</option>
                  <option>LightGBM</option>
                  <option>Gradient Boosting</option>
                  <option>Decision Tree</option>
                  <option>Deep Neural Network</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-text-muted mb-1">Epochs / Trees</label>
                  <input type="number" value={config.epochs} onChange={e => setConfig({...config, epochs: parseInt(e.target.value)||0})} disabled={isTraining} className="w-full bg-card border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-text-muted mb-1">Max Depth</label>
                  <input type="number" value={config.max_depth} onChange={e => setConfig({...config, max_depth: parseInt(e.target.value)||0})} disabled={isTraining} className="w-full bg-card border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-blue-500" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Live Dashboard Panel */}
        <div className="col-span-12 xl:col-span-8 flex flex-col h-[600px]">
          <div className="glass-panel flex-1 flex flex-col p-6 overflow-hidden relative">
            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase flex items-center gap-2">
              <Activity size={16} className={isTraining ? "text-blue-500 animate-pulse" : ""} /> Live Training Dashboard
            </h3>
            
            {!isTraining ? (
              <div className="flex-1 flex flex-col items-center justify-center opacity-50">
                <Activity size={64} className="text-text-muted mb-4" />
                <p className="text-text-muted font-mono tracking-widest text-sm">WAITING FOR TRAINING RUN</p>
              </div>
            ) : (
              <div className="flex-1 flex flex-col space-y-6">
                
                {/* Progress Bar & ETA */}
                <div className="bg-card rounded-xl p-4 border border-border relative overflow-hidden">
                  <div className="flex justify-between items-end mb-2">
                    <div>
                      <p className="text-xs font-bold text-blue-400 mb-1">EPOCH {trainingProgress.epoch} / {trainingProgress.total_epochs}</p>
                      <p className="text-2xl font-light text-text-primary">{((trainingProgress.epoch/trainingProgress.total_epochs)*100).toFixed(1)}%</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs font-bold text-text-muted mb-1">REMAINING</p>
                      <p className="text-xl font-mono text-text-primary">{trainingProgress.remaining_time}s</p>
                    </div>
                  </div>
                  <div className="w-full bg-card rounded-full h-2 overflow-hidden">
                    <div className="bg-blue-500 h-2 rounded-full shadow-[0_0_10px_rgba(59,130,246,0.8)] transition-all duration-300" style={{ width: `${(trainingProgress.epoch/trainingProgress.total_epochs)*100}%` }} />
                  </div>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-4 gap-4">
                  <div className="bg-card rounded-xl p-4 border border-border">
                    <p className="text-xs font-bold text-text-muted mb-1">TRAIN LOSS</p>
                    <p className="text-xl font-mono text-red-400">{trainingProgress.current_loss.toFixed(4)}</p>
                  </div>
                  <div className="bg-card rounded-xl p-4 border border-border">
                    <p className="text-xs font-bold text-text-muted mb-1">VAL ACCURACY</p>
                    <p className="text-xl font-mono text-green-400">{(trainingProgress.val_score * 100).toFixed(2)}%</p>
                  </div>
                  <div className="bg-card rounded-xl p-4 border border-border">
                    <p className="text-xs font-bold text-text-muted mb-1">CPU USAGE</p>
                    <p className="text-xl font-mono text-yellow-400">{trainingProgress.cpu_usage}%</p>
                  </div>
                  <div className="bg-card rounded-xl p-4 border border-border">
                    <p className="text-xs font-bold text-text-muted mb-1">RAM USAGE</p>
                    <p className="text-xl font-mono text-purple-400">{trainingProgress.memory_usage}%</p>
                  </div>
                </div>

                {/* Training Logs */}
                <div className="flex-1 bg-card rounded-xl border border-border p-4 overflow-hidden flex flex-col">
                  <p className="text-xs font-bold text-text-muted mb-2 font-mono">SYSTEM LOGS</p>
                  <div className="flex-1 font-mono text-xs text-green-500 flex items-end">
                    <p className="animate-pulse">&gt; {trainingProgress.log}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
