import React, { useState } from 'react';
import { useOperations } from '../hooks/useOperations';
import { Settings, Activity, HardDrive, Shield, Wrench, Server } from 'lucide-react';

import { SystemHealthView } from './SystemHealthView';
import { StorageBackupView } from './StorageBackupView';
import { SecurityLogView } from './SecurityLogView';
import { ConfigDeployView } from './ConfigDeployView';
import { DiagnosticsOptimizationView } from './DiagnosticsOptimizationView';

export const OperationsDashboard: React.FC = () => {
  const opsState = useOperations();
  const [activeTab, setActiveTab] = useState('health');

  const tabs = [
    { id: 'health', label: 'Health & Performance', icon: Activity, desc: 'Monitor CPU, RAM, Latency & Services' },
    { id: 'storage', label: 'Storage & Backups', icon: HardDrive, desc: 'Manage disk space and system snapshots' },
    { id: 'security', label: 'Security & Logs', icon: Shield, desc: 'Audit logs, access control & alerts' },
    { id: 'config', label: 'Config & Deploy', icon: Server, desc: 'System settings and release management' },
    { id: 'diagnostics', label: 'Diagnostics & Opt', icon: Wrench, desc: 'Automated fixes and health reports' },
  ];

  return (
    <div className="flex-1 flex overflow-hidden">
      <div className="w-72 bg-background-secondary/80 border-r border-border/50 flex flex-col backdrop-blur-md">
        <div className="p-6 border-b border-border/50">
          <h2 className="text-xl font-bold tracking-widest text-text-primary mb-1 flex items-center gap-2">
            <Settings className="text-yellow-500 animate-[spin_10s_linear_infinite]" /> OPERATIONS
          </h2>
          <p className="text-xs text-text-muted font-mono">Enterprise Command Center</p>
        </div>
        
        <div className="flex-1 overflow-y-auto px-4 py-4 space-y-2 custom-scrollbar">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-start gap-4 p-4 rounded-xl transition-all duration-200 text-left relative ${
                activeTab === tab.id 
                  ? 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/30 shadow-[inset_0_0_15px_rgba(234,179,8,0.1)]' 
                  : 'text-text-muted hover:bg-foreground/5 hover:text-text-primary border border-transparent'
              }`}
            >
              <tab.icon size={20} className={`mt-0.5 ${activeTab === tab.id ? 'text-yellow-400' : 'text-text-muted'}`} />
              <div>
                <span className="font-bold text-sm block mb-1">{tab.label}</span>
                <span className={`text-[10px] leading-tight block ${activeTab === tab.id ? 'text-yellow-400/70' : 'text-text-muted'}`}>
                  {tab.desc}
                </span>
              </div>
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto overflow-x-hidden p-6 custom-scrollbar bg-[#020617]">
        {activeTab === 'health' && <SystemHealthView opsState={opsState} />}
        {activeTab === 'storage' && <StorageBackupView opsState={opsState} />}
        {activeTab === 'security' && <SecurityLogView />}
        {activeTab === 'config' && <ConfigDeployView />}
        {activeTab === 'diagnostics' && <DiagnosticsOptimizationView opsState={opsState} />}
      </div>
    </div>
  );
};
