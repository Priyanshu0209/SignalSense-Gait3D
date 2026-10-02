import React from 'react';
import { Shield, Key, AlertOctagon, Terminal } from 'lucide-react';

export const SecurityLogView: React.FC = () => {
  return (
    <div className="space-y-6">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-2">
          <Shield className="text-red-500" /> Security & Logs
        </h2>
        <p className="text-text-muted text-sm">Audit trails, access control, and system event logging.</p>
      </div>

      <div className="grid grid-cols-3 gap-6 mb-6">
        <div className="glass-panel p-5 border-t-2 border-green-500 flex items-center gap-4">
          <div className="p-3 bg-green-500/10 rounded-lg">
            <Key className="text-green-500" size={24} />
          </div>
          <div>
            <p className="text-xs font-bold text-text-muted">ACTIVE SESSIONS</p>
            <p className="text-2xl font-light text-text-primary">4</p>
          </div>
        </div>
        <div className="glass-panel p-5 border-t-2 border-red-500 flex items-center gap-4">
          <div className="p-3 bg-red-500/10 rounded-lg">
            <AlertOctagon className="text-red-500" size={24} />
          </div>
          <div>
            <p className="text-xs font-bold text-text-muted">FAILED LOGINS (24H)</p>
            <p className="text-2xl font-light text-text-primary">0</p>
          </div>
        </div>
      </div>

      <div className="glass-panel overflow-hidden flex flex-col h-96">
        <div className="p-4 border-b border-border bg-card flex justify-between items-center">
          <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase flex items-center gap-2">
            <Terminal size={14} /> Live Audit Log
          </h3>
          <div className="flex gap-2">
            <select className="bg-card text-xs text-text-primary p-1 rounded border border-border">
              <option>All Sources</option>
              <option>API</option>
              <option>Auth</option>
              <option>System</option>
            </select>
          </div>
        </div>
        <div className="flex-1 bg-[#0a0a0a] p-4 font-mono text-xs overflow-y-auto custom-scrollbar space-y-1">
          <div className="text-green-400">[SYSTEM] Operations Center initialized.</div>
          <div className="text-blue-400">[AUTH] Admin token verified.</div>
          <div className="text-text-muted">[API] GET /api/v1/operations/metrics 200 OK</div>
          <div className="text-text-muted">[API] GET /api/v1/operations/services 200 OK</div>
          <div className="text-text-muted animate-pulse mt-4">Waiting for incoming logs...</div>
        </div>
      </div>
    </div>
  );
};
