import React, { useState } from 'react';
import { useLocalization } from '../hooks/useLocalization';
import { useAITraining } from '../hooks/useAITraining';
import { Map, PlayCircle, BarChart2 } from 'lucide-react';
import { LocalizationMap } from './LocalizationMap';
import { ReplayController } from './ReplayController';
import { MetricsOverlay } from './MetricsOverlay';
import { ModelSelector } from './ModelSelector';
import { BenchmarkStudio } from './BenchmarkStudio';

export const LocalizationDashboard: React.FC = () => {
  const locState = useLocalization();
  const aiState = useAITraining();
  
  const [activeTab, setActiveTab] = useState<'replay' | 'benchmark'>('replay');

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden bg-[#020617] p-6 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-3">
            <Map className="text-blue-500" /> AI Localization Studio
          </h2>
          <p className="text-text-muted text-sm">Validate models, map prediction errors, and run benchmarks.</p>
        </div>
        <div className="flex items-center gap-2 bg-card rounded-lg p-1 border border-border">
          <button 
            onClick={() => setActiveTab('replay')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'replay' ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:text-text-primary'}`}
          >
            <PlayCircle size={16} /> Replay & Map
          </button>
          <button 
            onClick={() => setActiveTab('benchmark')}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-bold transition-all ${activeTab === 'benchmark' ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:text-text-primary'}`}
          >
            <BarChart2 size={16} /> Benchmark Mode
          </button>
        </div>
      </div>

      {activeTab === 'replay' && (
        <div className="flex-1 grid grid-cols-12 gap-6 min-h-0">
          <div className="col-span-8 flex flex-col gap-6 h-full">
            <div className="flex justify-between items-center bg-card p-4 rounded-xl border border-border">
              <ModelSelector aiState={aiState} />
              <ReplayController locState={locState} aiState={aiState} />
            </div>
            
            <div className="flex-1 glass-panel relative overflow-hidden flex items-center justify-center min-h-[400px]">
              <LocalizationMap frame={locState.replayFrame} />
            </div>
          </div>
          
          <div className="col-span-4 h-full">
            <MetricsOverlay frame={locState.replayFrame} />
          </div>
        </div>
      )}

      {activeTab === 'benchmark' && (
        <BenchmarkStudio locState={locState} aiState={aiState} />
      )}
    </div>
  );
};
