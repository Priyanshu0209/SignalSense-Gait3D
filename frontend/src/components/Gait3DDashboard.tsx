import React, { useState } from 'react';
import { useGait3D } from '../hooks/useGait3D';
import { useNetworkData } from '../hooks/useNetworkData';
import { Scene3DViewer } from './Scene3DViewer';
import { GaitAnalyticsPanel } from './GaitAnalyticsPanel';
import { ActivityRecognitionHub } from './ActivityRecognitionHub';
import { Activity, Radio } from 'lucide-react';
import { useEffect } from 'react';

export const Gait3DDashboard: React.FC = () => {
  const {
    activities,
    metrics,
    sceneFrame,
    simulationEnabled,
    toggleSimulation,
  } = useGait3D();

  // Topology's live device list — used to drive the sync badge in Scene3DViewer
  const { onlineDevices: topologyDevices } = useNetworkData();

  const [activeSubTab, setActiveSubTab] = useState<'3d_kinematics'>('3d_kinematics');

  useEffect(() => {
    // Start in real topology mode by default instead of simulation
    toggleSimulation(false);
  }, []);

  return (
    <div className="w-full h-full flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-1">
      
      {/* Top Studio Sub-Navigation Bar */}
      <div className="glass-panel p-2 rounded-2xl border border-border shrink-0 flex items-center justify-between px-6 bg-background-secondary/60 backdrop-blur-md">
        <div className="flex items-center gap-2">
          <span className="px-3 py-1.5 rounded-xl bg-gradient-to-r from-blue-600 to-cyan-500 text-text-primary font-black text-xs tracking-widest shadow-[0_0_20px_rgba(6,182,212,0.4)] mr-2">
            RESEARCH BRANCH
          </span>
          <h2 className="text-sm font-bold tracking-widest text-text-primary">SIGNALSENSE-GAIT3D STUDIO</h2>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setActiveSubTab('3d_kinematics')}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-xs font-bold tracking-wider transition-all ${
              activeSubTab === '3d_kinematics'
                ? 'bg-accent-primary/10 text-accent-primary border border-accent-primary shadow-[0_0_20px_rgba(var(--accent-primary-rgb),0.3)]'
                : 'text-text-muted hover:bg-card-hover hover:text-text-primary border border-transparent'
            }`}
          >
            <Activity size={16} className={activeSubTab === '3d_kinematics' ? 'text-accent-primary animate-pulse' : 'text-text-muted'} />
            3D KINEMATIC & CADENCE LAB
          </button>


        </div>

        <div className="hidden xl:flex items-center gap-2 text-xs font-mono text-text-muted">
          <Radio size={14} className="text-status-success animate-pulse" />
          <span>Stream: <strong className="text-status-success">LIVE (20Hz)</strong></span>
        </div>
      </div>

      {/* Main Content Render Area */}
      <div className="flex-1 w-full space-y-6">
        {activeSubTab === '3d_kinematics' && (
          <>
            <Scene3DViewer 
              sceneFrame={sceneFrame} 
              onToggleSimulation={toggleSimulation} 
              simulationEnabled={simulationEnabled}
              topologyDevices={topologyDevices}
            />
            <GaitAnalyticsPanel metrics={metrics} topologyDevices={topologyDevices} />
            <ActivityRecognitionHub activities={activities} topologyDevices={topologyDevices} />
          </>
        )}


      </div>

    </div>
  );
};
