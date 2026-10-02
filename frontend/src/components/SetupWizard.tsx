import React, { useState } from 'react';
import { Wifi, Save, Server, Loader2, KeyRound, MonitorSmartphone } from 'lucide-react';

interface SetupWizardProps {
  onComplete: (config: any) => void;
}

export const SetupWizard: React.FC<SetupWizardProps> = ({ onComplete }) => {
  const [formData, setFormData] = useState({
    host: '192.168.1.1',
    username: 'root',
    password: 'admin',
    port: '22',
    brand: 'Netgear'
  });
  const [isTesting, setIsTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleTestAndSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsTesting(true);
    setError(null);

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const res = await fetch(`${API_URL}/operations/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!res.ok) {
        throw new Error('Failed to save configuration.');
      }

      // Check if backend connected successfully
      const healthRes = await fetch(`${API_URL.replace('/api/v1', '')}/health?t=${Date.now()}`);
      if (healthRes.ok) {
        const healthData = await healthRes.json();
        if (healthData.router_status === 'connected') {
            onComplete(formData);
        } else {
            throw new Error(`Router connection failed (${healthData.router_status}). Check credentials.`);
        }
      } else {
        throw new Error('Backend failed to respond.');
      }
    } catch (err: any) {
      setError(err.message || 'Connection failed. Please verify credentials.');
    } finally {
      setIsTesting(false);
    }
  };

  return (
    <div className="min-h-screen bg-background-primary flex flex-col items-center justify-center p-6 text-text-primary">
      <div className="max-w-md w-full bg-background-secondary border border-border rounded-2xl shadow-xl overflow-hidden">
        
        <div className="p-6 border-b border-border bg-card">
          <div className="flex items-center justify-center mb-4">
            <div className="p-3 bg-accent-primary/10 rounded-2xl text-accent-primary animate-pulse shadow-[0_0_30px_rgba(var(--accent-primary-rgb),0.3)]">
              <MonitorSmartphone size={32} />
            </div>
          </div>
          <h2 className="text-2xl font-black text-center tracking-wide">First Time Setup</h2>
          <p className="text-sm text-text-muted text-center mt-2 font-medium">
            Configure your enterprise router to begin live tracking.
          </p>
        </div>

        <form onSubmit={handleTestAndSave} className="p-6 space-y-5">
          {error && (
            <div className="p-3 rounded-xl bg-status-error/10 border border-status-error/30 text-status-error text-sm font-semibold flex items-start gap-2">
              <Server size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label className="block text-xs font-bold text-text-muted mb-1.5 ml-1">Router IP Address</label>
              <div className="relative">
                <Wifi size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <input
                  type="text"
                  value={formData.host}
                  onChange={(e) => setFormData({...formData, host: e.target.value})}
                  className="w-full bg-background-primary border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent-primary transition-colors"
                  required
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1.5 ml-1">SSH Username</label>
                <input
                  type="text"
                  value={formData.username}
                  onChange={(e) => setFormData({...formData, username: e.target.value})}
                  className="w-full bg-background-primary border border-border rounded-xl px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent-primary transition-colors"
                  required
                />
              </div>
              <div>
                <label className="block text-xs font-bold text-text-muted mb-1.5 ml-1">SSH Port</label>
                <input
                  type="text"
                  value={formData.port}
                  onChange={(e) => setFormData({...formData, port: e.target.value})}
                  className="w-full bg-background-primary border border-border rounded-xl px-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent-primary transition-colors"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold text-text-muted mb-1.5 ml-1">SSH Password</label>
              <div className="relative">
                <KeyRound size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                <input
                  type="password"
                  value={formData.password}
                  onChange={(e) => setFormData({...formData, password: e.target.value})}
                  className="w-full bg-background-primary border border-border rounded-xl pl-10 pr-4 py-2.5 text-sm font-mono focus:outline-none focus:border-accent-primary transition-colors"
                  required
                />
              </div>
            </div>
          </div>

          <div className="pt-4">
            <button
              type="submit"
              disabled={isTesting}
              className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-black text-sm transition-all ${
                isTesting 
                  ? 'bg-card-hover text-text-muted cursor-not-allowed' 
                  : 'bg-accent-primary text-text-primary shadow-lg hover:shadow-accent-primary/25 hover:-translate-y-0.5'
              }`}
            >
              {isTesting ? (
                <><Loader2 size={18} className="animate-spin" /> TESTING CONNECTION...</>
              ) : (
                <><Save size={18} /> SAVE & CONNECT</>
              )}
            </button>
          </div>
        </form>

      </div>
    </div>
  );
};
