import React from 'react';
import { GitCommit } from 'lucide-react';

export const ModelSelector: React.FC<{ aiState: any }> = ({ aiState }) => {
  const { models, activateModel } = aiState;
  
  const activeModel = models.find((m: any) => m.status === 'Active');

  return (
    <div className="flex items-center gap-4">
      <GitCommit className={activeModel ? 'text-green-500' : 'text-text-muted'} size={20} />
      <select 
        value={activeModel?.id || ''}
        onChange={(e) => {
          if (e.target.value) activateModel(e.target.value);
        }}
        className="bg-card border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-blue-500 w-64"
      >
        <option value="">Select AI Model...</option>
        {models.map((m: any) => (
          <option key={m.id} value={m.id}>{m.name} ({m.accuracy}%)</option>
        ))}
      </select>
    </div>
  );
};
