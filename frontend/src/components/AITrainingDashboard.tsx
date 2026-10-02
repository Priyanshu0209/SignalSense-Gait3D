import React, { useState, useEffect } from 'react';
import { useAITraining } from '../hooks/useAITraining';
import { Database, Filter, Sliders, BrainCircuit, Activity, BarChart2, GitCommit, Target } from 'lucide-react';

import { DatasetManagerView } from './DatasetManagerView';
import { ModelTrainingView } from './ModelTrainingView';
import { ModelEvaluationView } from './ModelEvaluationView';
import { ModelRegistryView } from './ModelRegistryView';
import { LiveInferenceView } from './LiveInferenceView';

export const AITrainingDashboard: React.FC = () => {
  const aiState = useAITraining();
  const [activeTab, setActiveTab] = useState('dataset');
  const [selectedDataset, setSelectedDataset] = useState<string | null>(null);
  const datasets = aiState.datasets || [];

  useEffect(() => {
    if (datasets.length > 0 && (!selectedDataset || !datasets.find((d: any) => d.name === selectedDataset))) {
      setSelectedDataset(datasets[0].name);
    }
  }, [datasets, selectedDataset]);

  const tabs = [
    { id: 'dataset', label: 'Dataset Manager', icon: Database },
    { id: 'cleaning', label: 'Data Cleaning', icon: Filter },
    { id: 'features', label: 'Feature Engineering', icon: Sliders },
    { id: 'training', label: 'Model Training', icon: BrainCircuit },
    { id: 'evaluation', label: 'Evaluation', icon: BarChart2 },
    { id: 'registry', label: 'Model Registry', icon: GitCommit },
    { id: 'inference', label: 'Live Inference', icon: Target },
  ];

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Left Sub-Navigation */}
      <div className="w-64 bg-background-secondary/50 border-r border-border/50 flex flex-col backdrop-blur-md">
        <div className="p-6">
          <h2 className="text-xl font-bold tracking-widest text-text-primary mb-1 flex items-center gap-2">
            <BrainCircuit className="text-blue-500" /> AI LAB
          </h2>
          <p className="text-xs text-text-muted font-mono">Distance Estimation</p>
        </div>
        
        <div className="flex-1 overflow-y-auto px-4 py-2 space-y-2 custom-scrollbar">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 text-left ${
                activeTab === tab.id 
                  ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30 shadow-[inset_0_0_15px_rgba(59,130,246,0.1)]' 
                  : 'text-text-muted hover:bg-foreground/5 hover:text-text-primary border border-transparent'
              }`}
            >
              <tab.icon size={18} className={activeTab === tab.id ? 'text-blue-400' : 'text-text-muted'} />
              <span className="font-bold text-sm tracking-wide">{tab.label}</span>
            </button>
          ))}
        </div>
        
        {aiState.trainingProgress && (
          <div className="p-4 border-t border-border/50">
            <div className="bg-blue-900/30 rounded-xl p-3 border border-blue-500/30 relative overflow-hidden">
              <div className="absolute inset-0 bg-blue-500/10 animate-pulse" />
              <div className="relative flex items-center gap-2 mb-2">
                <Activity size={16} className="text-blue-400 animate-bounce" />
                <span className="text-xs font-bold text-blue-400">TRAINING ACTIVE</span>
              </div>
              <div className="w-full bg-card rounded-full h-1.5 mb-1">
                <div 
                  className="bg-blue-500 h-1.5 rounded-full" 
                  style={{ width: `${(aiState.trainingProgress.epoch / aiState.trainingProgress.total_epochs) * 100}%` }} 
                />
              </div>
              <div className="flex justify-between text-[10px] text-text-muted font-mono">
                <span>Ep {aiState.trainingProgress.epoch}/{aiState.trainingProgress.total_epochs}</span>
                <span>{aiState.trainingProgress.remaining_time.toFixed(0)}s left</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 custom-scrollbar bg-[#020617]">
        {datasets.length === 0 && activeTab !== 'dataset' ? (
          <div className="h-full flex flex-col items-center justify-center text-text-muted italic p-6 text-center">
            No datasets found in the registry. <br/> Please collect data in the Dataset Manager module first.
          </div>
        ) : (
          <>
            {activeTab === 'dataset' && <DatasetManagerView aiState={aiState} />}
            {activeTab === 'cleaning' && (
              <div className="glass-panel p-12 text-center text-text-muted">
                <Filter className="w-16 h-16 mx-auto mb-4 text-text-muted" />
                <h2 className="text-xl font-bold mb-2 text-text-primary">Data Cleaning Engine</h2>
                <p>Automatically detect and remove missing values, outliers, and duplicates.</p>
                <button className="btn-primary mt-6 px-6 py-2 rounded-lg font-bold text-sm">Run Auto-Clean</button>
              </div>
            )}
            {activeTab === 'features' && (
              <div className="glass-panel p-12 text-center text-text-muted">
                <Sliders className="w-16 h-16 mx-auto mb-4 text-text-muted" />
                <h2 className="text-xl font-bold mb-2 text-text-primary">Feature Engineering</h2>
                <p>Generate time-series aggregates, SNR calculations, and encodings.</p>
                <button className="btn-primary mt-6 px-6 py-2 rounded-lg font-bold text-sm">Generate Features</button>
              </div>
            )}
            {activeTab === 'training' && <ModelTrainingView aiState={aiState} />}
            {activeTab === 'evaluation' && <ModelEvaluationView aiState={aiState} />}
            {activeTab === 'registry' && <ModelRegistryView aiState={aiState} />}
            {activeTab === 'inference' && <LiveInferenceView aiState={aiState} />}
          </>
        )}
      </div>
    </div>
  );
};
