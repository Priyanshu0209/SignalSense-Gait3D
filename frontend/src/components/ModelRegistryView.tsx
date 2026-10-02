import React from 'react';
import { GitCommit, Play, Trash2, Download } from 'lucide-react';

export const ModelRegistryView: React.FC<{ aiState: any }> = ({ aiState }) => {
  const { models, activateModel, deleteModel } = aiState;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider">Model Registry</h2>
          <p className="text-text-muted text-sm">Manage trained models and deploy them for live inference.</p>
        </div>
        <button onClick={aiState.refreshData} className="px-4 py-2 bg-card hover:bg-card-hover text-text-primary rounded-lg text-sm font-bold transition-colors">
          REFRESH
        </button>
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-left text-sm text-text-primary">
          <thead className="bg-card text-text-muted text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4">Model Name</th>
              <th className="px-6 py-4">Algorithm</th>
              <th className="px-6 py-4">Dataset</th>
              <th className="px-6 py-4">Accuracy</th>
              <th className="px-6 py-4">Status</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-foreground/5">
            {models.map((m: any) => (
              <tr key={m.id} className="hover:bg-foreground/5 transition-colors group">
                <td className="px-6 py-4 font-medium text-text-primary flex items-center gap-3">
                  <GitCommit size={16} className={m.status === 'Active' ? 'text-green-500' : 'text-blue-500'} />
                  {m.name}
                  <span className="text-xs bg-card px-2 py-0.5 rounded text-text-muted font-mono">{m.version}</span>
                </td>
                <td className="px-6 py-4">{m.algorithm}</td>
                <td className="px-6 py-4 text-xs font-mono text-text-muted truncate max-w-[150px]">{m.dataset}</td>
                <td className="px-6 py-4 font-mono text-green-400">{m.accuracy}%</td>
                <td className="px-6 py-4">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${m.status === 'Active' ? 'bg-green-500/20 text-green-400 border border-green-500/30' : 'bg-card text-text-muted'}`}>
                    {m.status.toUpperCase()}
                  </span>
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    {m.status !== 'Active' && (
                      <button onClick={() => activateModel(m.id)} className="p-2 bg-card hover:bg-green-600 text-text-primary hover:text-text-primary rounded-lg transition-colors" title="Activate for Inference">
                        <Play size={14} />
                      </button>
                    )}
                    <button className="p-2 bg-card hover:bg-card-hover text-text-primary hover:text-text-primary rounded-lg transition-colors" title="Export Model (.pkl, ONNX)">
                      <Download size={14} />
                    </button>
                    <button onClick={() => deleteModel(m.id)} className="p-2 bg-card hover:bg-red-600 text-text-primary hover:text-text-primary rounded-lg transition-colors" title="Delete">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {models.length === 0 && (
              <tr>
                <td colSpan={6} className="px-6 py-12 text-center text-text-muted italic">
                  No models trained yet. Go to Model Training to create one.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
