import React from 'react';
import { Server, Sliders, Box, Upload } from 'lucide-react';

export const ConfigDeployView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-2">
          <Server className="text-indigo-500" /> Configuration & Deployment
        </h2>
        <p className="text-text-muted text-sm">Manage global settings, environments, and deployment packages.</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="glass-panel p-6">
          <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-6 flex items-center gap-2">
            <Sliders size={16} className="text-indigo-400" /> Global Configuration
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-text-muted mb-1">DATASET STORAGE PATH</label>
              <input type="text" disabled value="/home/signalsense/Datasets" className="w-full bg-card border border-border rounded p-2 text-sm text-text-primary font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-text-muted mb-1">MODEL REGISTRY PATH</label>
              <input type="text" disabled value="/home/signalsense/Models" className="w-full bg-card border border-border rounded p-2 text-sm text-text-primary font-mono" />
            </div>
            <div>
              <label className="block text-xs font-bold text-text-muted mb-1">LOG RETENTION DAYS</label>
              <input type="number" disabled value={30} className="w-full bg-card border border-border rounded p-2 text-sm text-text-primary font-mono" />
            </div>
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase mb-6 flex items-center gap-2">
            <Box size={16} className="text-indigo-400" /> Deployment Manager
          </h3>
          <p className="text-sm text-text-muted mb-6">Current Environment: <span className="font-bold text-green-400">PRODUCTION</span></p>
          
          <div className="space-y-4">
            <button className="w-full flex items-center justify-center gap-2 py-3 bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 border border-indigo-500/30 rounded-lg font-bold transition-colors">
              <Upload size={18} /> EXPORT DEPLOYMENT PACKAGE
            </button>
            <button className="w-full flex items-center justify-center gap-2 py-3 bg-card hover:bg-card-hover text-text-primary rounded-lg font-bold transition-colors">
              IMPORT CONFIGURATION
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
