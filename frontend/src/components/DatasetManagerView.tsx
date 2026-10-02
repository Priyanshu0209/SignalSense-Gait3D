import React from 'react';
import { FileSpreadsheet, Download, Trash2, Settings2 } from 'lucide-react';

export const DatasetManagerView: React.FC<{ aiState: any }> = ({ aiState }) => {
  const { datasets } = aiState;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider">Dataset Manager</h2>
          <p className="text-text-muted text-sm">Select and prepare datasets for model training.</p>
        </div>
        <button onClick={aiState.refreshData} className="px-4 py-2 bg-card hover:bg-card-hover text-text-primary rounded-lg text-sm font-bold transition-colors">
          REFRESH
        </button>
      </div>

      <div className="glass-panel overflow-hidden">
        <table className="w-full text-left text-sm text-text-primary">
          <thead className="bg-card text-text-muted text-xs uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4">Dataset Name</th>
              <th className="px-6 py-4">Samples</th>
              <th className="px-6 py-4">Size</th>
              <th className="px-6 py-4">Environment</th>
              <th className="px-6 py-4">Quality Score</th>
              <th className="px-6 py-4">Date</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-foreground/5">
            {datasets.map((ds: any) => (
              <tr key={ds.filename} className="hover:bg-foreground/5 transition-colors group">
                <td className="px-6 py-4 font-medium text-text-primary flex items-center gap-3">
                  <FileSpreadsheet size={16} className="text-blue-500" />
                  {ds.name || ds.filename.replace('.csv', '')}
                </td>
                <td className="px-6 py-4 font-mono">{ds.samples?.toLocaleString() || 'N/A'}</td>
                <td className="px-6 py-4 font-mono">{ds.size_mb} MB</td>
                <td className="px-6 py-4">{ds.environment}</td>
                <td className="px-6 py-4">
                  <div className="flex items-center gap-2">
                    <div className="w-16 h-1.5 bg-card rounded-full overflow-hidden">
                      <div className={`h-full ${ds.quality_score > 80 ? 'bg-green-500' : ds.quality_score > 50 ? 'bg-yellow-500' : 'bg-red-500'}`} style={{ width: `${ds.quality_score}%` }} />
                    </div>
                    <span className="text-xs font-mono">{ds.quality_score}/100</span>
                  </div>
                </td>
                <td className="px-6 py-4 font-mono text-xs text-text-muted">
                  {new Date(ds.created_at).toLocaleDateString()}
                </td>
                <td className="px-6 py-4 text-right">
                  <div className="flex items-center justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button className="p-2 bg-card hover:bg-blue-600 text-text-primary hover:text-text-primary rounded-lg transition-colors" title="Preview & Settings">
                      <Settings2 size={14} />
                    </button>
                    <button 
                      onClick={() => aiState.downloadDataset(ds.filename)}
                      className="p-2 bg-card hover:bg-card-hover text-text-primary hover:text-text-primary rounded-lg transition-colors" title="Export">
                      <Download size={14} />
                    </button>
                    <button 
                      onClick={() => {
                        if (confirm(`Are you sure you want to delete dataset ${ds.name}?`)) {
                          aiState.deleteDataset(ds.filename);
                        }
                      }}
                      className="p-2 bg-card hover:bg-red-600 text-text-primary hover:text-text-primary rounded-lg transition-colors" title="Delete">
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {datasets.length === 0 && (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-text-muted italic">
                  No datasets found. Run Dataset Collection first.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
