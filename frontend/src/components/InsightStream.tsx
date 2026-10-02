import React, { useEffect, useState } from 'react';
import { Activity, ShieldAlert, Zap } from 'lucide-react';

interface Insight {
  timestamp: string;
  message: string;
  confidence: number;
  type: 'warning' | 'success' | 'info';
}

interface Scores {
  overall: number;
  security: number;
  performance: number;
  reliability: number;
}

export const InsightStream = () => {
  const [insights, setInsights] = useState<Insight[]>([]);
  const [scores, setScores] = useState<Scores>({ overall: 0, security: 0, performance: 0, reliability: 0 });

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
        const res = await fetch(`${API_URL}/analytics/insights`);
        const data = await res.json();
        setInsights(data.feed);
        setScores(data.scores);
      } catch (err) {
        // Silent failure for periodic poll
      }
    };
    
    fetchInsights();
    const interval = setInterval(fetchInsights, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="w-full h-full flex flex-col gap-4">
      
      {/* Network Score Panel */}
      <div className="bg-background-secondary/80 backdrop-blur-md border border-border rounded-2xl p-4 shadow-xl">
        <h3 className="text-xs font-bold text-text-muted tracking-widest uppercase mb-4">Network Score</h3>
        
        <div className="flex items-center justify-between mb-4 pb-4 border-b border-border">
          <span className="text-3xl font-black text-text-primary">{scores.overall.toFixed(0)}</span>
          <div className="h-10 w-10 rounded-full border-4 border-blue-500 flex items-center justify-center">
            <Activity size={18} className="text-blue-500"/>
          </div>
        </div>

        <div className="space-y-3">
          <ScoreRow label="Security" value={scores.security} icon={<ShieldAlert size={14} className="text-green-400" />} />
          <ScoreRow label="Performance" value={scores.performance} icon={<Zap size={14} className="text-yellow-400" />} />
          <ScoreRow label="Reliability" value={scores.reliability} icon={<Activity size={14} className="text-blue-400" />} />
        </div>
      </div>

      {/* Insight Stream */}
      <div className="bg-background-secondary/80 backdrop-blur-md border border-border rounded-2xl p-4 shadow-xl flex-1 min-h-0 flex flex-col">
        <h3 className="text-xs font-bold text-text-muted tracking-widest uppercase mb-4">Live Insights</h3>
        <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-1">
          {insights.length === 0 ? (
            <p className="text-xs text-text-muted italic">Listening for insights...</p>
          ) : (
            insights.map((insight, idx) => (
              <div key={idx} className="bg-card border border-border rounded-lg p-3 relative overflow-hidden">
                <div className={`absolute left-0 top-0 bottom-0 w-1 ${insight.type === 'warning' ? 'bg-red-500' : 'bg-green-500'}`} />
                <p className="text-xs text-text-primary leading-relaxed mb-2">{insight.message}</p>
                <div className="flex justify-between items-center text-[10px] text-text-muted font-mono">
                  <span>{new Date(insight.timestamp).toLocaleTimeString()}</span>
                  <span>Conf: {insight.confidence}%</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
      
    </div>
  );
};

const ScoreRow = ({ label, value, icon }: { label: string, value: number, icon: React.ReactNode }) => (
  <div className="flex justify-between items-center">
    <div className="flex items-center gap-2">
      {icon}
      <span className="text-xs text-text-primary font-medium">{label}</span>
    </div>
    <span className="text-xs font-bold text-text-primary font-mono">{value.toFixed(0)}</span>
  </div>
);
