import React from 'react';
import { Target, Zap, ShieldCheck, Activity } from 'lucide-react';

export const ModelEvaluationView: React.FC<{ aiState: any }> = ({ aiState }) => {
  const { experiments } = aiState;
  
  // Sort by start_time descending
  const sortedExp = [...experiments].sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime());
  const latest = sortedExp.find(e => e.status === 'Completed');

  if (!latest) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center h-full text-text-muted">
        <Target size={64} className="mb-4 text-text-secondary" />
        <h2 className="text-xl font-bold mb-2">No Evaluation Data</h2>
        <p>Complete a model training run to view evaluation metrics.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-text-primary tracking-wider">Model Evaluation</h2>
          <p className="text-text-muted text-sm">Detailed performance metrics for the latest experiment ({latest.id}).</p>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <MetricCard title="Test Accuracy" value={`${latest.metrics.Accuracy}%`} icon={<Target />} color="text-green-400" />
        <MetricCard title="R² Score" value={latest.metrics.R2} icon={<ShieldCheck />} color="text-blue-400" />
        <MetricCard title="MAE (Meters)" value={latest.metrics.MAE} icon={<Activity />} color="text-yellow-400" />
        <MetricCard title="RMSE (Meters)" value={latest.metrics.RMSE} icon={<Zap />} color="text-red-400" />
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div className="glass-panel p-6 min-h-[300px] flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-tr from-blue-900/20 to-transparent" />
          <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase absolute top-6 left-6">Predicted vs Actual</h3>
          <p className="text-text-muted italic text-sm mt-8">Interactive chart visualization would render here (Recharts/Chart.js)</p>
        </div>
        <div className="glass-panel p-6 min-h-[300px] flex flex-col items-center justify-center relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-tl from-purple-900/20 to-transparent" />
          <h3 className="text-sm font-bold tracking-wider text-text-muted mb-4 uppercase absolute top-6 left-6">Feature Importance</h3>
          <p className="text-text-muted italic text-sm mt-8">Bar chart of feature SHAP values would render here</p>
        </div>
      </div>

      <div className="glass-panel overflow-hidden mt-6">
        <div className="p-4 border-b border-border bg-card">
          <h3 className="text-sm font-bold tracking-wider text-text-muted uppercase">Experiment History</h3>
        </div>
        <table className="w-full text-left text-sm text-text-primary">
          <thead className="bg-card text-text-muted text-xs uppercase">
            <tr>
              <th className="px-6 py-3">Experiment ID</th>
              <th className="px-6 py-3">Algorithm</th>
              <th className="px-6 py-3">Dataset</th>
              <th className="px-6 py-3">Accuracy</th>
              <th className="px-6 py-3">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-foreground/5">
            {sortedExp.map(exp => (
              <tr key={exp.id} className="hover:bg-foreground/5">
                <td className="px-6 py-3 font-mono text-xs">{exp.id}</td>
                <td className="px-6 py-3">{exp.algorithm}</td>
                <td className="px-6 py-3 truncate max-w-[200px]">{exp.dataset}</td>
                <td className="px-6 py-3 font-mono text-green-400">{exp.metrics.Accuracy ? `${exp.metrics.Accuracy}%` : '-'}</td>
                <td className="px-6 py-3">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${exp.status === 'Completed' ? 'bg-green-500/20 text-green-400' : exp.status === 'Running' ? 'bg-blue-500/20 text-blue-400' : 'bg-red-500/20 text-red-400'}`}>
                    {exp.status}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const MetricCard = ({ title, value, icon, color }: any) => (
  <div className="glass-panel p-6 flex items-center justify-between">
    <div>
      <p className="text-xs font-bold text-text-muted mb-1">{title}</p>
      <p className={`text-3xl font-light ${color}`}>{value}</p>
    </div>
    <div className={`p-4 bg-card rounded-full ${color} opacity-80`}>
      {React.cloneElement(icon, { size: 24 })}
    </div>
  </div>
);
