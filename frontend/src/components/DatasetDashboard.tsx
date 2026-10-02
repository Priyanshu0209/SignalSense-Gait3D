import React, { useState } from 'react';
import { ConnectedDevice } from '../hooks/useNetworkData';
import { useDatasetCollection } from '../hooks/useDatasetCollection';
import { PolarMap } from './PolarMap';
import { DeviceGroundTruth } from './DeviceGroundTruth';
import { CoverageHeatmap } from './CoverageHeatmap';
import { Play, Pause, Square, Settings } from 'lucide-react';

interface DatasetDashboardProps {
  devices: ConnectedDevice[];
}

export const DatasetDashboard: React.FC<DatasetDashboardProps> = ({ devices }) => {
  const {
    config,
    updateConfig,
    groundTruths,
    updateGroundTruth,
    state,
    liveSamples,
    startCollection,
    pauseCollection,
    resumeCollection,
    stopCollection
  } = useDatasetCollection(devices);

  const [activeTab, setActiveTab] = useState<'setup' | 'live' | 'heatmap'>('setup');
  const [isStarting, setIsStarting] = useState(false);

  const handleStart = async () => {
    setIsStarting(true);
    await startCollection();
    // Simulate server acknowledgement delay
    setTimeout(() => setIsStarting(false), 500);
  };

  const formatDuration = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = Math.floor(seconds % 60);
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 space-y-6">
      {/* Header & Controls */}
      <div className="flex items-center justify-between bg-background-secondary/50 p-6 rounded-2xl border border-border/50 backdrop-blur-md">
        <div>
          <h2 className="text-2xl font-bold tracking-widest text-text-primary mb-2">DATASET COLLECTION</h2>
          <p className="text-text-muted text-sm">Collect real-world signal data with ground truth for ML training.</p>
        </div>
        <div className="flex gap-4">
          {state.status === 'Stopped' && (
            <button onClick={handleStart} disabled={isStarting} className={`btn-primary flex items-center gap-2 px-6 py-3 rounded-lg font-bold shadow-[0_0_15px_rgba(22,163,74,0.4)] ${isStarting ? 'bg-card-hover text-text-muted' : 'bg-green-600 hover:bg-green-500 text-text-primary'}`}>
              <Play size={20} /> {isStarting ? 'STARTING...' : 'START COLLECTION'}
            </button>
          )}
          {state.status === 'Running' && (
            <button onClick={pauseCollection} className="btn-secondary flex items-center gap-2 bg-yellow-600/20 text-yellow-500 border border-yellow-500/50 px-6 py-3 rounded-lg font-bold">
              <Pause size={20} /> PAUSE
            </button>
          )}
          {state.status === 'Paused' && (
            <button onClick={resumeCollection} className="btn-primary flex items-center gap-2 bg-green-600 hover:bg-green-500 text-text-primary px-6 py-3 rounded-lg font-bold">
              <Play size={20} /> RESUME
            </button>
          )}
          {(state.status === 'Running' || state.status === 'Paused') && (
            <button onClick={stopCollection} className="btn-danger flex items-center gap-2 bg-red-600/20 hover:bg-red-600/40 text-red-500 border border-red-500/50 px-6 py-3 rounded-lg font-bold shadow-[0_0_15px_rgba(220,38,38,0.3)]">
              <Square size={20} /> STOP & SAVE
            </button>
          )}
        </div>
      </div>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-12 gap-6">
        
        {/* Left Column: Status & Setup */}
        <div className="col-span-12 xl:col-span-4 space-y-6">
          {/* Status Panel */}
          <div className="glass-panel p-6">
            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase">Collector Status</h3>
            <div className="flex items-center gap-3 mb-6">
              <div className={`w-3 h-3 rounded-full ${state.status === 'Running' ? 'bg-green-500 neon-glow' : state.status === 'Paused' ? 'bg-yellow-500' : 'bg-slate-500'}`} />
              <span className={`font-bold tracking-widest ${state.status === 'Running' ? 'text-green-500' : state.status === 'Paused' ? 'text-yellow-500' : 'text-text-muted'}`}>{state.status.toUpperCase()}</span>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-card p-4 rounded-xl border border-border">
                <p className="text-xs text-text-muted mb-1 font-bold">SAMPLES COLLECTED</p>
                <p className="text-2xl font-light text-text-primary">{state.total_samples.toLocaleString()}</p>
              </div>
              <div className="bg-card p-4 rounded-xl border border-border">
                <p className="text-xs text-text-muted mb-1 font-bold">SESSION DURATION</p>
                <p className="text-2xl font-light text-text-primary">{formatDuration(state.duration)}</p>
              </div>
              <div className="bg-card p-4 rounded-xl border border-border">
                <p className="text-xs text-text-muted mb-1 font-bold">QUALITY SCORE</p>
                <p className="text-2xl font-light text-blue-400">{state.quality.quality_score}%</p>
              </div>
              <div className="bg-card p-4 rounded-xl border border-border">
                <p className="text-xs text-text-muted mb-1 font-bold">AVG RSSI</p>
                <p className="text-2xl font-light text-purple-400">{state.quality.avg_rssi} dBm</p>
              </div>
            </div>
          </div>

          {/* Configuration Panel */}
          <div className="glass-panel p-6">
            <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase flex items-center gap-2"><Settings size={16} /> Session Setup</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1">Session Name</label>
                <input type="text" value={config.session_name} onChange={e => updateConfig({ session_name: e.target.value })} disabled={state.status !== 'Stopped'} className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500" />
              </div>
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1">Environment</label>
                <select value={config.environment} onChange={e => updateConfig({ environment: e.target.value })} disabled={state.status !== 'Stopped'} className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500">
                  <option>Indoor - Office</option>
                  <option>Indoor - Home</option>
                  <option>Outdoor - Open</option>
                  <option>Outdoor - Urban</option>
                  <option>Warehouse</option>
                </select>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-bold text-text-muted mb-1">Samples / Device</label>
                  <input type="number" value={config.samples_per_device} onChange={e => updateConfig({ samples_per_device: parseInt(e.target.value) || 0 })} disabled={state.status !== 'Stopped'} className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500" />
                </div>
                <div>
                  <label className="block text-xs font-bold text-text-muted mb-1">Interval (sec)</label>
                  <input type="number" step="0.5" value={config.sampling_interval} onChange={e => updateConfig({ sampling_interval: parseFloat(e.target.value) || 1 })} disabled={state.status !== 'Stopped'} className="w-full bg-card border border-border rounded-lg p-2.5 text-sm text-text-primary focus:outline-none focus:border-blue-500" />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Visualization & Data */}
        <div className="col-span-12 xl:col-span-8 flex flex-col space-y-6">
          <div className="flex items-center gap-2 border-b border-border pb-2">
            <button onClick={() => setActiveTab('setup')} className={`px-4 py-2 text-sm font-bold tracking-wider rounded-t-lg transition-colors ${activeTab === 'setup' ? 'text-blue-400 border-b-2 border-blue-500' : 'text-text-muted hover:text-text-primary'}`}>GROUND TRUTH</button>
            <button onClick={() => setActiveTab('live')} className={`px-4 py-2 text-sm font-bold tracking-wider rounded-t-lg transition-colors ${activeTab === 'live' ? 'text-blue-400 border-b-2 border-blue-500' : 'text-text-muted hover:text-text-primary'}`}>LIVE SAMPLES</button>
            <button onClick={() => setActiveTab('heatmap')} className={`px-4 py-2 text-sm font-bold tracking-wider rounded-t-lg transition-colors ${activeTab === 'heatmap' ? 'text-blue-400 border-b-2 border-blue-500' : 'text-text-muted hover:text-text-primary'}`}>COVERAGE HEATMAP</button>
          </div>

          <div className="flex-1 bg-background-secondary/50 rounded-2xl border border-border/50 backdrop-blur-md p-6 overflow-hidden flex flex-col min-h-[500px]">
            {activeTab === 'setup' && (
              <div className="flex flex-col xl:flex-row gap-6 h-full">
                <div className="flex-1 overflow-hidden flex flex-col">
                  <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase">Device Configuration</h3>
                  <DeviceGroundTruth 
                    devices={devices} 
                    groundTruths={groundTruths} 
                    onUpdate={updateGroundTruth}
                    disabled={state.status !== 'Stopped'}
                  />
                </div>
                <div className="flex-1 flex flex-col">
                  <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase">Interactive Polar Map</h3>
                  <div className="flex-1 bg-card rounded-xl border border-border relative overflow-hidden flex items-center justify-center p-4">
                    <PolarMap devices={devices} groundTruths={groundTruths} onUpdate={updateGroundTruth} disabled={state.status !== 'Stopped'} />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'live' && (
              <div className="flex flex-col h-full overflow-hidden">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-bold tracking-wider text-text-muted uppercase">Live Data Stream</h3>
                  <span className="text-xs text-blue-400 font-mono">Auto-saving to CSV</span>
                </div>
                <div className="flex-1 overflow-auto rounded-xl border border-border/50 custom-scrollbar">
                  <table className="w-full text-left text-sm text-text-primary">
                    <thead className="text-xs uppercase bg-card/80 text-text-muted sticky top-0 backdrop-blur-sm shadow-md">
                      <tr>
                        <th className="px-4 py-3">Time</th>
                        <th className="px-4 py-3">Device</th>
                        <th className="px-4 py-3">Dist (m)</th>
                        <th className="px-4 py-3">Dir (°)</th>
                        <th className="px-4 py-3">RSSI</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-800/50">
                      {liveSamples.length === 0 ? (
                        <tr><td colSpan={7} className="px-4 py-8 text-center text-text-muted italic">No samples collected yet.</td></tr>
                      ) : (
                        liveSamples.map((s, i) => (
                          <tr key={i} className="hover:bg-card/30 transition-colors">
                            <td className="px-4 py-2 font-mono text-xs">{new Date(s.Timestamp).toLocaleTimeString()}</td>
                            <td className="px-4 py-2 font-medium">{s['Device Name']}</td>
                            <td className="px-4 py-2 text-blue-400">{s['Ground Truth Distance'].toFixed(2)}</td>
                            <td className="px-4 py-2 text-purple-400">{s['Ground Truth Direction']}</td>
                            <td className="px-4 py-2 font-mono">{s.RSSI} dBm</td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}

            {activeTab === 'heatmap' && (
              <div className="flex flex-col h-full">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-sm font-bold tracking-wider text-text-muted uppercase">Dataset Coverage</h3>
                  <span className="text-xs text-text-muted">Green indicates collected combinations</span>
                </div>
                <div className="flex-1 overflow-auto flex items-center justify-center p-4">
                  <CoverageHeatmap matrix={state.coverage_matrix} />
                </div>
              </div>
            )}

          </div>
        </div>
      </div>
    </div>
  );
};
