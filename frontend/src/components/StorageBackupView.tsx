import React from 'react';
import { HardDrive, Save, UploadCloud, Archive } from 'lucide-react';

export const StorageBackupView: React.FC<{ opsState: any }> = ({ opsState }) => {
  const { metrics, backups, createBackup, restoreBackup } = opsState;

  if (!metrics) return null;

  return (
    <div className="space-y-6">
      <div className="mb-8 flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-2">
            <HardDrive className="text-blue-500" /> Storage & Backup Manager
          </h2>
          <p className="text-text-muted text-sm">Monitor disk space and manage system snapshots.</p>
        </div>
        <button onClick={() => createBackup('Full System')} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-text-primary px-4 py-2 rounded-lg text-sm font-bold transition-colors shadow-[0_0_15px_rgba(37,99,235,0.4)]">
          <Save size={16} /> CREATE BACKUP
        </button>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Storage Breakdown */}
        <div className="col-span-4 glass-panel p-6 flex flex-col justify-between">
          <div>
            <h3 className="text-xs font-bold tracking-wider text-text-muted mb-6 uppercase">Physical Disk Usage</h3>
            <div className="relative w-48 h-48 mx-auto flex items-center justify-center">
              <svg className="w-full h-full transform -rotate-90">
                <circle cx="96" cy="96" r="88" fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="16" />
                <circle 
                  cx="96" cy="96" r="88" 
                  fill="none" 
                  stroke="#3b82f6" 
                  strokeWidth="16" 
                  strokeDasharray={`${(metrics.disk_usage / 100) * (2 * Math.PI * 88)} ${(2 * Math.PI * 88)}`} 
                  className="transition-all duration-1000"
                />
              </svg>
              <div className="absolute text-center">
                <p className="text-3xl font-light text-text-primary">{metrics.disk_usage}%</p>
                <p className="text-xs text-text-muted font-bold tracking-widest">USED</p>
              </div>
            </div>
          </div>
          <div className="space-y-2 mt-8">
            <div className="flex justify-between text-sm">
              <span className="text-text-muted">Datasets</span>
              <span className="font-mono text-text-primary">45%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-muted">Models</span>
              <span className="font-mono text-text-primary">30%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-text-muted">Logs</span>
              <span className="font-mono text-text-primary">15%</span>
            </div>
          </div>
        </div>

        {/* Backup List */}
        <div className="col-span-8 glass-panel overflow-hidden flex flex-col">
          <div className="p-5 border-b border-border flex justify-between items-center bg-card">
            <h3 className="text-xs font-bold tracking-wider text-text-muted uppercase">System Snapshots</h3>
          </div>
          <div className="flex-1 overflow-auto custom-scrollbar">
            <table className="w-full text-left text-sm text-text-primary">
              <thead className="bg-card text-text-muted text-xs uppercase tracking-wider sticky top-0">
                <tr>
                  <th className="px-6 py-4">Backup ID</th>
                  <th className="px-6 py-4">Date</th>
                  <th className="px-6 py-4">Size</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-foreground/5">
                {backups.map((bak: any) => (
                  <tr key={bak.id} className="hover:bg-foreground/5 transition-colors">
                    <td className="px-6 py-4 font-bold text-text-primary flex items-center gap-2">
                      <Archive size={14} className="text-text-muted" /> {bak.id}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs text-text-muted">
                      {new Date(bak.timestamp * 1000).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 font-mono text-xs">{bak.size_mb} MB</td>
                    <td className="px-6 py-4">
                      <span className="px-2 py-1 rounded text-[10px] font-bold tracking-wider uppercase bg-green-500/10 text-green-400 border border-green-500/20">
                        {bak.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <button onClick={() => restoreBackup(bak.id)} className="p-1.5 bg-orange-500/20 hover:bg-orange-500/40 text-orange-400 rounded transition-colors" title="Restore">
                        <UploadCloud size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
                {backups.length === 0 && (
                  <tr><td colSpan={5} className="p-6 text-center text-text-muted italic">No backups found.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
