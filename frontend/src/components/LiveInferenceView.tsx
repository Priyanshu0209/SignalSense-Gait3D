import React from 'react';
import { Target, Activity } from 'lucide-react';

export const LiveInferenceView: React.FC<{ aiState: any }> = ({ aiState }) => {
  const { liveInferences, models } = aiState;
  const inferencesArray = Object.values(liveInferences);
  
  const activeModel = models.find((m: any) => m.status === 'Active');

  return (
    <div className="space-y-6 flex flex-col h-full">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider flex items-center gap-3">
            <Target className="text-red-500 animate-pulse" /> Live Inference Engine
          </h2>
          <p className="text-text-muted text-sm">Real-time distance estimation using active AI model.</p>
        </div>
        {activeModel ? (
          <div className="bg-green-500/10 border border-green-500/30 px-4 py-2 rounded-lg flex items-center gap-3">
            <Activity size={16} className="text-green-400 animate-pulse" />
            <div>
              <p className="text-xs text-green-500/70 font-bold uppercase">Active Model</p>
              <p className="text-sm font-mono text-green-400">{activeModel.name}</p>
            </div>
          </div>
        ) : (
          <div className="bg-red-500/10 border border-red-500/30 px-4 py-2 rounded-lg text-red-400 text-sm font-bold">
            No Active Model
          </div>
        )}
      </div>

      <div className="glass-panel flex-1 overflow-hidden flex flex-col">
        <table className="w-full text-left text-sm text-text-primary">
          <thead className="bg-card text-text-muted text-xs uppercase tracking-wider sticky top-0 z-10 backdrop-blur-md">
            <tr>
              <th className="px-6 py-4">Device</th>
              <th className="px-6 py-4">MAC Address</th>
              <th className="px-6 py-4">Est. Distance (m)</th>
              <th className="px-6 py-4">Confidence</th>
              <th className="px-6 py-4">Quality</th>
              <th className="px-6 py-4 text-right">Inference Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-foreground/5">
            {inferencesArray.map((inf: any) => (
              <tr key={inf.mac_address} className="hover:bg-foreground/5 transition-colors">
                <td className="px-6 py-4 font-medium text-text-primary">{inf.hostname}</td>
                <td className="px-6 py-4 font-mono text-xs text-text-muted">{inf.mac_address}</td>
                <td className="px-6 py-4">
                  <span className="text-2xl font-light text-blue-400">{inf.estimated_distance.toFixed(2)}</span>
                  <span className="text-text-muted ml-1">m</span>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-24 h-1.5 bg-card rounded-full overflow-hidden">
                      <div className={`h-full ${inf.confidence_pct > 80 ? 'bg-green-500' : inf.confidence_pct > 60 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${inf.confidence_pct}%` }} />
                    </div>
                    <span className="text-xs font-mono">{inf.confidence_pct}%</span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${inf.quality === 'High' ? 'bg-green-500/20 text-green-400' : inf.quality === 'Medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'}`}>
                    {inf.quality}
                  </span>
                </td>
                <td className="px-6 py-4 text-right font-mono text-xs text-text-muted">
                  {inf.inference_time_ms} ms
                </td>
              </tr>
            ))}
            {inferencesArray.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-text-muted italic">
                  {activeModel ? "Waiting for live device signals..." : "Please activate a model in the Registry to start inference."}
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
