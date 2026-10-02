import { useState } from 'react';
import { Play, Pause, FastForward, Rewind, SkipBack, Clock } from 'lucide-react';

export const PlaybackControls = () => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [speed, setSpeed] = useState(1);
  const [progress, setProgress] = useState(100); // 100 = Live

  const isLive = progress === 100;

  return (
    <div className="glass-card p-4 flex flex-col gap-3 shadow-xl absolute bottom-6 right-6 z-40 w-[480px]">
      
      <div className="flex items-center gap-3">
        <Clock size={16} className={isLive ? "text-blue-400" : "text-orange-400"} />
        <span className="text-xs font-bold tracking-widest text-text-primary">
          {isLive ? "LIVE TELEMETRY" : "HISTORICAL PLAYBACK"}
        </span>
        
        {!isLive && (
          <span className="text-xs font-mono text-orange-300 ml-auto bg-orange-950/50 px-2 py-0.5 rounded">
            2026-07-22 14:05:00
          </span>
        )}
      </div>

      <div className="flex items-center gap-4">
        <button className="text-text-muted hover:text-text-primary transition-colors" title="Jump Back">
          <SkipBack size={18} />
        </button>
        <button className="text-text-muted hover:text-text-primary transition-colors" title="Rewind">
          <Rewind size={18} />
        </button>
        
        <button 
          onClick={() => setIsPlaying(!isPlaying)}
          className="w-10 h-10 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center text-text-primary transition-colors shadow-[0_0_15px_rgba(59,130,246,0.5)]"
        >
          {isPlaying ? <Pause size={20} /> : <Play size={20} className="ml-1" />}
        </button>
        
        <button 
          onClick={() => setSpeed(s => s === 1 ? 2 : s === 2 ? 4 : 1)}
          className="text-text-muted hover:text-text-primary transition-colors font-bold font-mono text-sm w-8 flex justify-center"
          title="Speed"
        >
          {speed}x
        </button>
        <button className="text-text-muted hover:text-text-primary transition-colors" title="Fast Forward">
          <FastForward size={18} />
        </button>
        
        <div className="flex-1 relative group cursor-pointer ml-2">
          <input 
            type="range" 
            min="0" 
            max="100" 
            value={progress}
            onChange={(e) => setProgress(Number(e.target.value))}
            className="w-full h-2 bg-card rounded-lg appearance-none cursor-pointer accent-blue-500"
          />
        </div>
        
        <button 
          onClick={() => setProgress(100)}
          className={`px-3 py-1 rounded text-xs font-bold tracking-widest transition-colors ${isLive ? 'bg-blue-600 text-text-primary' : 'bg-card text-text-muted hover:bg-card-hover'}`}
        >
          LIVE
        </button>
      </div>
    </div>
  );
};
