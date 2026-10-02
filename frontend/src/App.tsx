import { useState, useEffect } from 'react';
import { useNetworkData, ConnectedDevice } from './hooks/useNetworkData';
import { NetworkMap } from './components/NetworkMap';
import { NetworkTopology } from './components/NetworkTopology';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { NetworkInsights } from './components/NetworkInsights';
import { DatasetDashboard } from './components/DatasetDashboard';
import { ResearchDashboard } from './components/ResearchDashboard';
import { OperationsDashboard } from './components/OperationsDashboard';
import { Gait3DDashboard } from './components/Gait3DDashboard';
import { SettingsPanel } from './components/SettingsPanel';
import { CommandPalette } from './components/CommandPalette';
import { RouterDashboard } from './components/RouterDashboard';
import { DevicePanel } from './components/DevicePanel';
import { ExplanationPanel } from './components/ExplanationPanel';
import { PlaybackControls } from './components/PlaybackControls';
import { AICopilot } from './components/AICopilot';
import { InsightStream } from './components/InsightStream';
import { Timeline } from './components/Timeline';
import { RouterInfo } from './components/RouterInfo';
import { SetupWizard } from './components/SetupWizard';
import { ThemeProvider } from './contexts/ThemeContext';
import { 
  Loader2, Bot, FlaskConical, Bell, Settings,
  Activity, Wifi, Box, Database, Search, Layers, Server, Shield
} from 'lucide-react';

function AppContent() {
  const { devices, routerStatus, events, isConnected, addEvent } = useNetworkData();
  const [selectedDevice, setSelectedDevice] = useState<ConnectedDevice | null>(null);
  const [isDiagnosticsRunning, setIsDiagnosticsRunning] = useState(false);
  const [isRouterInfoOpen, setIsRouterInfoOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);
  const [isExplanationOpen, setIsExplanationOpen] = useState(false);
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [semanticFilter, setSemanticFilter] = useState('');
  const [currentView, setCurrentView] = useState<'radar' | 'topology' | 'analytics' | 'dataset' | 'research' | 'operations' | 'gait3d' | 'settings'>('gait3d');
  
  const [isConfiguring, setIsConfiguring] = useState(true);

  // Fetch config on startup
  useEffect(() => {
    const checkConfig = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
        const res = await fetch(`${API_URL}/operations/config`);
        if (res.ok) {
          const config = await res.json();
          if (config && config.host) {
            setIsConfiguring(false);
          } else {
            setIsConfiguring(true);
          }
        } else {
          setIsConfiguring(true);
        }
      } catch (err) {
        setIsConfiguring(true);
      }
    };
    checkConfig();
  }, []);
  
  // Current Time for Header
  const [currentTime, setCurrentTime] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Semantic filtering logic
  const filteredDevices = devices.filter(d => {
    if (!semanticFilter) return true;
    const filter = semanticFilter.toLowerCase();
    
    if (filter === 'unstable') return d.health_score === 'Poor' || d.health_score === 'Critical';
    if (filter === 'streaming') return d.behavior_profile === 'Streaming';
    if (filter === 'gaming') return d.behavior_profile === 'Workstation/Gaming';
    if (filter === 'iot') return (d.device_type || '').toLowerCase().includes('iot') || d.behavior_profile === 'IoT Device';
    if (filter === 'offline') return !d.online_status;
    
    return (d.hostname || '').toLowerCase().includes(filter) || (d.mac_address || '').toLowerCase().includes(filter);
  });

  const handleRunDiagnostics = async () => {
    setIsDiagnosticsRunning(true);
    addEvent('info', 'Started router diagnostics...');
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const res = await fetch(`${API_URL}/diagnostics/run`, { method: 'POST' });
      if (res.ok) {
        addEvent('success', 'Diagnostics completed successfully.');
      } else {
        addEvent('error', 'Diagnostics failed.');
      }
    } catch (e) {
      addEvent('error', 'Failed to reach diagnostics endpoint.');
    } finally {
      setIsDiagnosticsRunning(false);
    }
  };

  const isRouterOnline = isConnected && routerStatus?.connection_status === 'Connected';
  const statusColorClass = isRouterOnline ? 'bg-status-success neon-glow-success' : 'bg-status-error neon-glow-red';

  const toggleSimulation = async (action: string) => {
    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      await fetch(`${API_URL}/analytics/simulation`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action })
      });
    } catch (e) {
      console.error(e);
    }
  };

  const isSimulating = devices.some(d => d.twin_mode === 'SIMULATION');

  const navigationItems = [
    { id: 'gait3d', label: '3D Twin', icon: Box },
    { id: 'radar', label: 'Radar Map', icon: Wifi },
    { id: 'topology', label: 'Topology', icon: Layers },
    { id: 'analytics', label: 'Analytics', icon: Activity },
    { id: 'dataset', label: 'Dataset', icon: Database },

    { id: 'operations', label: 'Operations', icon: Server },
    { id: 'research', label: 'Observatory', icon: Shield },
    { id: 'settings', label: 'Settings', icon: Settings },
  ] as const;

  if (isConfiguring) {
    return <SetupWizard onComplete={() => setIsConfiguring(false)} />;
  }

  return (
    <div className="w-screen h-screen overflow-hidden flex font-sans bg-background-primary text-text-primary">
      
      {/* SIMULATION OVERLAY */}
      {isSimulating && (
        <div className="fixed inset-0 pointer-events-none border-[4px] border-status-warning/30 z-[100]">
          <div className="absolute top-6 left-1/2 -translate-x-1/2 bg-status-warning/90 backdrop-blur-lg text-black px-6 py-2 rounded-full font-bold tracking-widest text-sm shadow-neon-amber animate-pulse flex items-center gap-3 pointer-events-auto">
            <FlaskConical size={18} /> DIGITAL TWIN SIMULATION
            <button onClick={() => toggleSimulation('stop')} className="ml-4 bg-card hover:bg-card text-black px-4 py-1 rounded-full text-xs transition-colors">
              TERMINATE
            </button>
          </div>
        </div>
      )}

      {/* ENTERPRISE SIDEBAR */}
      <div className="w-20 hover:w-64 transition-all duration-300 group z-50 flex flex-col bg-background-secondary/80 backdrop-blur-2xl border-r border-border h-full py-6 shrink-0 absolute lg:relative">
        <div className="flex items-center px-6 mb-10 overflow-hidden">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-accent-primary to-accent-secondary flex items-center justify-center shadow-neon-blue shrink-0">
            <span className="font-bold text-lg text-text-primary">S</span>
          </div>
          <span className="ml-4 font-bold tracking-widest text-lg whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">
            SIGNALSENSE
          </span>
        </div>

        <div className="flex-1 overflow-y-auto custom-scrollbar flex flex-col gap-2 px-3">
          {navigationItems.map(item => {
            const Icon = item.icon;
            const isActive = currentView === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentView(item.id as any)}
                className={`flex items-center px-3 py-3 rounded-xl transition-all duration-300 group/item relative overflow-hidden ${
                  isActive 
                    ? 'bg-accent-primary/10 text-accent-primary border border-accent-primary/20 shadow-glass-hover' 
                    : 'text-text-muted hover:text-text-primary hover:bg-white/5'
                }`}
              >
                {isActive && <div className="absolute left-0 top-0 bottom-0 w-1 bg-accent-primary shadow-neon-blue" />}
                <Icon size={22} className="shrink-0" />
                <span className="ml-4 font-semibold tracking-wide whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  {item.label}
                </span>
              </button>
            );
          })}
        </div>

        <div className="mt-auto px-3 flex flex-col gap-2">
          <button 
            onClick={() => setIsCopilotOpen(true)}
            className="flex items-center px-3 py-3 rounded-xl text-purple-400 hover:bg-purple-500/10 border border-transparent hover:border-purple-500/20 transition-all duration-300"
          >
            <Bot size={22} className="shrink-0" />
            <span className="ml-4 font-bold tracking-wide whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              AI COPILOT
            </span>
          </button>
        </div>
      </div>

      {/* MAIN CONTENT AREA */}
      <div className="flex-1 flex flex-col h-full relative pl-20 lg:pl-0 transition-all duration-300">
        
        {/* TOP HEADER */}
        <header className="h-20 shrink-0 border-b border-border bg-background-primary/50 backdrop-blur-xl flex items-center justify-between px-8 z-40">
          <div className="flex items-center gap-6">
            <h1 className="text-xl font-medium text-text-primary tracking-wide">
              {navigationItems.find(i => i.id === currentView)?.label.toUpperCase()} <span className="text-text-muted font-light ml-2">/ DASHBOARD</span>
            </h1>
          </div>

          <div className="flex items-center gap-6">
            <div className="hidden md:flex items-center gap-3 px-4 py-2 bg-card/40 border border-border rounded-full text-sm font-medium text-text-secondary">
              <span className="text-text-muted font-mono">{currentTime.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' }).toUpperCase()}</span>
              <span className="text-accent-secondary font-mono tracking-wider">{currentTime.toLocaleTimeString('en-US', { hour12: false })}</span>
            </div>

            <button 
              onClick={() => setIsCommandPaletteOpen(true)}
              className="flex items-center gap-3 px-4 py-2 bg-card border border-border hover:border-accent-primary/30 hover:bg-card-hover rounded-full text-sm font-medium transition-all group"
            >
              <Search size={16} className="text-text-muted group-hover:text-accent-primary transition-colors" />
              <span className="text-text-muted hidden sm:block">Search / Command...</span>
              <span className="bg-background-secondary px-2 py-0.5 rounded text-xs text-text-muted ml-2">⌘K</span>
            </button>
            
            <button 
              onClick={() => setIsRouterInfoOpen(true)}
              className="relative p-2 text-text-muted hover:text-accent-secondary bg-card border border-border rounded-full hover:border-accent-secondary/30 transition-all"
            >
              <Activity size={18} />
              <div className={`absolute top-0 right-0 w-2.5 h-2.5 rounded-full ${statusColorClass} border-2 border-background-primary`} />
            </button>

            <button className="p-2 text-text-muted hover:text-text-primary bg-card border border-border rounded-full transition-all">
              <Bell size={18} />
            </button>
          </div>
        </header>

        {/* CONNECTION LOST BANNER */}
        {!isConnected && (
          <div className="bg-status-error/10 border-b border-status-error/30 p-2 text-center text-xs font-bold text-status-error tracking-widest backdrop-blur-md">
            CONNECTION TO BACKEND LOST. SYSTEM ATTEMPTING RECOVERY...
          </div>
        )}

        {/* DYNAMIC VIEWPORT & ROUTER WIDGETS */}
        <div className="flex-1 overflow-hidden flex gap-6 p-6">
          
          {/* Main Dashboard Canvas */}
          <main className={`flex-1 relative bg-card/20 border border-border rounded-3xl shadow-2xl ${currentView === 'gait3d' ? 'overflow-y-auto custom-scrollbar' : 'overflow-hidden flex flex-col'}`}>
            {currentView === 'radar' && (
              <>
                <div className="flex-1 relative min-h-0">
                  <NetworkMap devices={filteredDevices} routerStatus={routerStatus} onDeviceClick={setSelectedDevice} />
                </div>
                <div className="shrink-0">
                  <NetworkInsights routerStatus={routerStatus} devices={filteredDevices} />
                </div>
              </>
            )}
            {currentView === 'topology' && <NetworkTopology devices={filteredDevices} routerStatus={routerStatus} onDeviceClick={setSelectedDevice} />}
            {currentView === 'analytics' && <AnalyticsDashboard devices={filteredDevices} routerStatus={routerStatus} />}
            {currentView === 'dataset' && <DatasetDashboard devices={devices} />}

            {currentView === 'research' && <ResearchDashboard />}
            {currentView === 'operations' && <OperationsDashboard />}
            {currentView === 'settings' && <SettingsPanel />}
            {currentView === 'gait3d' && <Gait3DDashboard />}
            
            {isDiagnosticsRunning && (
              <div className="absolute inset-0 bg-background-primary/80 backdrop-blur-md z-30 flex flex-col items-center justify-center rounded-3xl">
                <Loader2 className="w-12 h-12 text-accent-primary animate-spin mb-4" />
                <p className="text-lg font-bold text-text-primary tracking-widest neon-glow-primary">EXECUTING DIAGNOSTICS</p>
              </div>
            )}
          </main>

          {/* Right Operations Column (Router + Timeline) */}
          <aside className="w-80 hidden xl:flex flex-col gap-6 shrink-0">
            <div className="flex-1 bg-card/30 border border-border rounded-3xl overflow-hidden glass-card">
              <RouterDashboard status={routerStatus} onRunDiagnostics={handleRunDiagnostics} />
            </div>
            
            {currentView === 'radar' && (
              <div className="flex-1 min-h-0">
                <InsightStream />
              </div>
            )}

            <div className="h-1/3 bg-card/30 border border-border rounded-3xl overflow-hidden glass-card p-4">
              <Timeline events={events} />
            </div>
          </aside>
        </div>
      </div>

      {/* OVERLAYS & MODALS */}
      <DevicePanel device={selectedDevice} onClose={() => setSelectedDevice(null)} onExplain={() => setIsExplanationOpen(true)} />
      <ExplanationPanel isOpen={isExplanationOpen} onClose={() => setIsExplanationOpen(false)} device={selectedDevice} />
      <RouterInfo isOpen={isRouterInfoOpen} onClose={() => setIsRouterInfoOpen(false)} status={routerStatus} />
      <AICopilot isOpen={isCopilotOpen} onClose={() => setIsCopilotOpen(false)} />
      <PlaybackControls />
      <CommandPalette isOpen={isCommandPaletteOpen} onClose={() => setIsCommandPaletteOpen(false)} onNavigate={setCurrentView} onSearch={setSemanticFilter} />
    </div>
  );
}

export default function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}
