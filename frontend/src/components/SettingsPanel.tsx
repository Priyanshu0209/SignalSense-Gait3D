import React, { useState, useEffect } from 'react';
import { useTheme } from '../contexts/ThemeContext';
import { Moon, Sun, Bell, Activity, Save, Globe, Download, Database, Monitor, Wifi } from 'lucide-react';
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export const SettingsPanel: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [hardwareAcceleration, setHardwareAcceleration] = useState(true);
  const [sessionTimeout, setSessionTimeout] = useState('30m');
  const [telemetryMode, setTelemetryMode] = useState('standard');
  const [language, setLanguage] = useState('en');
  
  // Router Config
  const [routerHost, setRouterHost] = useState('');
  const [routerUsername, setRouterUsername] = useState('');
  const [routerPassword, setRouterPassword] = useState('');
  const [saveStatus, setSaveStatus] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_URL}/operations/config`)
      .then(res => res.json())
      .then(data => {
        setRouterHost(data.host || '');
        setRouterUsername(data.username || '');
      })
      .catch(err => console.error("Failed to load config", err));
  }, []);

  const handleSavePreferences = async () => {
    setSaveStatus('Saving...');
    try {
        if (routerHost && routerUsername && routerPassword) {
            const res = await fetch(`${API_URL}/operations/config`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    host: routerHost,
                    username: routerUsername,
                    password: routerPassword
                })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Failed to save configuration.");
            }
        }
        setSaveStatus('Preferences Saved!');
        setTimeout(() => setSaveStatus(null), 3000);
    } catch (err: any) {
        setSaveStatus(`Error: ${err.message}`);
    }
  };

  const handleExportJSON = () => {
    alert("Exporting System State JSON...");
  };

  const handleExportCSV = () => {
    alert("Downloading Telemetry Logs CSV...");
  };

  return (
    <div className="w-full h-full flex flex-col gap-6 overflow-y-auto custom-scrollbar pr-1 pb-10">
      
      {/* Header */}
      <div className="glass-panel p-6 flex flex-col gap-2 shrink-0">
        <h2 className="text-xl font-bold tracking-tight">System Settings</h2>
        <p className="text-sm text-text-muted">Manage your application preferences, appearance, and data polling rates.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1 content-start">
        
        {/* Appearance Settings */}
        <div className="glass-card p-6 flex flex-col gap-6">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-accent-primary/10 rounded-lg text-accent-primary">
              {theme === 'dark' ? <Moon size={20} /> : <Sun size={20} />}
            </div>
            <h3 className="font-semibold tracking-wide">Appearance</h3>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Theme Mode</p>
              <p className="text-xs text-text-muted mt-1">Toggle between Light and Dark mode.</p>
            </div>
            <button 
              onClick={toggleTheme}
              className="px-4 py-2 bg-background-secondary border border-border rounded-lg text-sm font-semibold hover:bg-card-hover transition-colors flex items-center gap-2"
            >
              {theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            </button>
          </div>
        </div>

        {/* Router Settings */}
        <div className="glass-card p-6 flex flex-col gap-4">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
              <Wifi size={20} />
            </div>
            <h3 className="font-semibold tracking-wide">Router Configuration</h3>
          </div>
          
          <div className="flex flex-col gap-3">
            <div>
              <label className="text-xs font-medium text-text-muted mb-1 block">Router IP</label>
              <input 
                type="text" 
                value={routerHost}
                onChange={e => setRouterHost(e.target.value)}
                placeholder="192.168.1.1"
                className="w-full bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary"
              />
            </div>
            <div className="flex gap-4">
                <div className="flex-1">
                  <label className="text-xs font-medium text-text-muted mb-1 block">Username</label>
                  <input 
                    type="text" 
                    value={routerUsername}
                    onChange={e => setRouterUsername(e.target.value)}
                    placeholder="root"
                    className="w-full bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary"
                  />
                </div>
                <div className="flex-1">
                  <label className="text-xs font-medium text-text-muted mb-1 block">Password</label>
                  <input 
                    type="password" 
                    value={routerPassword}
                    onChange={e => setRouterPassword(e.target.value)}
                    placeholder="Enter to change"
                    className="w-full bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary"
                  />
                </div>
            </div>
          </div>
        </div>

        {/* System Settings */}
        <div className="glass-card p-6 flex flex-col gap-6">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-accent-secondary/10 rounded-lg text-accent-secondary">
              <Activity size={20} />
            </div>
            <h3 className="font-semibold tracking-wide">System & Polling</h3>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Data Refresh Rate</p>
              <p className="text-xs text-text-muted mt-1">How often the dashboard fetches new data.</p>
            </div>
            <select className="bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary">
              <option value="1s">Real-time (1s)</option>
              <option value="5s">Balanced (5s)</option>
              <option value="10s">Efficient (10s)</option>
            </select>
          </div>
        </div>

        {/* Notifications */}
        <div className="glass-card p-6 flex flex-col gap-6">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-status-warning/10 rounded-lg text-status-warning">
              <Bell size={20} />
            </div>
            <h3 className="font-semibold tracking-wide">Notifications</h3>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Alert Notifications</p>
              <p className="text-xs text-text-muted mt-1">Receive alerts for device disconnects and anomalies.</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" className="sr-only peer" defaultChecked />
              <div className="w-11 h-6 bg-background-secondary border border-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-border after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-primary"></div>
            </label>
          </div>
        </div>

        {/* Data & Telemetry */}
        <div className="glass-card p-6 flex flex-col gap-6">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-purple-500/10 rounded-lg text-purple-500">
              <Database size={20} />
            </div>
            <h3 className="font-semibold tracking-wide">Data & Telemetry</h3>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Telemetry Verbosity</p>
              <p className="text-xs text-text-muted mt-1">Control the detail level of SOC logs.</p>
            </div>
            <select 
              value={telemetryMode}
              onChange={(e) => setTelemetryMode(e.target.value)}
              className="bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary"
            >
              <option value="minimal">Minimal</option>
              <option value="standard">Standard</option>
              <option value="verbose">Verbose (Debug)</option>
            </select>
          </div>

          <div className="flex items-center justify-between mt-2">
            <div>
              <p className="font-medium text-sm">Hardware Acceleration</p>
              <p className="text-xs text-text-muted mt-1">Use GPU for 3D rendering and animations.</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" checked={hardwareAcceleration} onChange={() => setHardwareAcceleration(!hardwareAcceleration)} className="sr-only peer" />
              <div className="w-11 h-6 bg-background-secondary border border-border peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-accent-primary"></div>
            </label>
          </div>
        </div>

        {/* Security & Localization */}
        <div className="glass-card p-6 flex flex-col gap-6">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-500">
              <Globe size={20} />
            </div>
            <h3 className="font-semibold tracking-wide">Localization & Security</h3>
          </div>
          
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-sm">Dashboard Language</p>
              <p className="text-xs text-text-muted mt-1">Select your preferred language.</p>
            </div>
            <select 
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary"
            >
              <option value="en">English (US)</option>
              <option value="es">Español</option>
              <option value="hi">हिन्दी (Hindi)</option>
            </select>
          </div>

          <div className="flex items-center justify-between mt-2">
            <div>
              <p className="font-medium text-sm">Session Timeout</p>
              <p className="text-xs text-text-muted mt-1">Auto-lock dashboard after inactivity.</p>
            </div>
            <select 
              value={sessionTimeout}
              onChange={(e) => setSessionTimeout(e.target.value)}
              className="bg-background-secondary border border-border text-sm rounded-lg px-3 py-2 text-text-primary focus:outline-none focus:border-accent-primary"
            >
              <option value="15m">15 Minutes</option>
              <option value="30m">30 Minutes</option>
              <option value="1h">1 Hour</option>
              <option value="never">Never</option>
            </select>
          </div>
        </div>

        {/* Export Data */}
        <div className="glass-card p-6 flex flex-col gap-6 md:col-span-2">
          <div className="flex items-center gap-3 border-b border-border pb-4">
            <div className="p-2 bg-blue-500/10 rounded-lg text-blue-500">
              <Download size={20} />
            </div>
            <h3 className="font-semibold tracking-wide">Data Export</h3>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-4">
            <div className="flex-1">
              <p className="font-medium text-sm">Export System State</p>
              <p className="text-xs text-text-muted mt-1">Download a full JSON dump of the current topology and ML inference state for external analysis.</p>
            </div>
            <button 
              onClick={handleExportJSON}
              className="px-4 py-2 bg-background-secondary border border-border rounded-lg text-sm font-semibold hover:bg-card-hover transition-colors flex items-center gap-2 w-full sm:w-auto justify-center"
            >
              <Database size={16} />
              Export JSON
            </button>
            <button 
              onClick={handleExportCSV}
              className="px-4 py-2 bg-background-secondary border border-border rounded-lg text-sm font-semibold hover:bg-card-hover transition-colors flex items-center gap-2 w-full sm:w-auto justify-center"
            >
              <Monitor size={16} />
              Download CSV
            </button>
          </div>
        </div>

      </div>
      
      {/* Save Action */}
      <div className="flex justify-between items-center mt-auto pt-6">
        <div className="text-sm font-medium">
            {saveStatus && (
                <span className={saveStatus.includes('Error') ? 'text-red-500' : 'text-green-500'}>
                    {saveStatus}
                </span>
            )}
        </div>
        <button 
          onClick={handleSavePreferences}
          className="px-6 py-2.5 bg-accent-primary hover:bg-accent-primary/90 text-text-primary rounded-xl font-semibold flex items-center gap-2 transition-colors"
        >
          <Save size={18} />
          Save Preferences
        </button>
      </div>
      
    </div>
  );
};
