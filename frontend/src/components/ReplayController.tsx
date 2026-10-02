import React, { useEffect, useState } from 'react';
import { Play, Pause, Rewind, FastForward } from 'lucide-react';

export const ReplayController: React.FC<{ locState: any, aiState: any }> = ({ locState, aiState }) => {
  const { replayState, loadReplay, playReplay, pauseReplay, seekReplay, setSpeed } = locState;
  const { datasets } = aiState;
  
  const [selectedDataset, setSelectedDataset] = useState('');

  useEffect(() => {
    if (selectedDataset) {
      loadReplay(selectedDataset);
    }
  }, [selectedDataset]);

  if (!replayState) {
    return (
      <div className="flex items-center gap-4">
        <select 
          value={selectedDataset} 
          onChange={(e) => setSelectedDataset(e.target.value)}
          className="bg-card border border-border rounded-lg p-2 text-sm text-text-primary focus:outline-none focus:border-blue-500 w-64"
        >
          <option value="">Load Dataset for Replay...</option>
          {datasets.map((d: any) => <option key={d.filename} value={d.filename}>{d.name || d.filename}</option>)}
        </select>
      </div>
    );
  }



  return (
    <div className="flex items-center gap-4 flex-1 justify-end">
      <div className="flex items-center gap-2 bg-card px-3 py-1.5 rounded-lg border border-border">
        <button onClick={() => setSpeed(0.5)} className={`text-xs font-mono font-bold px-2 py-1 rounded ${replayState.speed === 0.5 ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:text-text-primary'}`}>0.5x</button>
        <button onClick={() => setSpeed(1.0)} className={`text-xs font-mono font-bold px-2 py-1 rounded ${replayState.speed === 1.0 ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:text-text-primary'}`}>1x</button>
        <button onClick={() => setSpeed(2.0)} className={`text-xs font-mono font-bold px-2 py-1 rounded ${replayState.speed === 2.0 ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:text-text-primary'}`}>2x</button>
        <button onClick={() => setSpeed(5.0)} className={`text-xs font-mono font-bold px-2 py-1 rounded ${replayState.speed === 5.0 ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:text-text-primary'}`}>5x</button>
      </div>

      <div className="flex items-center gap-2">
        <button onClick={() => seekReplay(Math.max(0, replayState.current_index - 10))} className="p-2 text-text-muted hover:text-text-primary transition-colors">
          <Rewind size={20} />
        </button>
        {replayState.is_playing ? (
          <button onClick={pauseReplay} className="p-2 bg-blue-600 hover:bg-blue-500 text-text-primary rounded-full transition-colors shadow-[0_0_15px_rgba(37,99,235,0.4)]">
            <Pause size={24} />
          </button>
        ) : (
          <button onClick={playReplay} className="p-2 bg-blue-600 hover:bg-blue-500 text-text-primary rounded-full transition-colors shadow-[0_0_15px_rgba(37,99,235,0.4)]">
            <Play size={24} className="ml-1" />
          </button>
        )}
        <button onClick={() => seekReplay(Math.min(replayState.total_samples, replayState.current_index + 10))} className="p-2 text-text-muted hover:text-text-primary transition-colors">
          <FastForward size={20} />
        </button>
      </div>

      <div className="flex items-center gap-4 flex-1 max-w-md ml-4">
        <span className="text-xs font-mono text-text-muted">{replayState.current_index}</span>
        <input 
          type="range" 
          min="0" 
          max={replayState.total_samples} 
          value={replayState.current_index} 
          onChange={(e) => seekReplay(parseInt(e.target.value))}
          className="flex-1 accent-blue-500"
        />
        <span className="text-xs font-mono text-text-muted">{replayState.total_samples}</span>
      </div>
      
      <button 
        onClick={() => { pauseReplay(); setSelectedDataset(''); }} 
        className="ml-4 text-xs font-bold text-red-400 hover:text-red-300 transition-colors"
      >
        CLOSE
      </button>
    </div>
  );
};
