import React from 'react';
import { PlayCircle, Flame, HardDrive, Sparkles, Clock, RefreshCw } from 'lucide-react';

export const TrainingProgressPanel: React.FC = () => {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-black uppercase tracking-[0.2em] text-text-primary flex items-center gap-2">
          <PlayCircle size={15} className="text-purple-400 animate-pulse" /> TRAINING WORKFLOW PROGRESS & HARDWARE TELEMETRY
        </h3>
        <div className="flex items-center gap-3">
          <span className="text-[11px] font-mono text-emerald-400 font-bold px-2.5 py-0.5 rounded-md bg-emerald-500/10 border border-emerald-500/30 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            STATUS: ACTIVE TRAINING
          </span>
          <span className="text-[11px] font-mono text-text-muted bg-background-secondary px-2.5 py-0.5 rounded border border-border">
            OPTIMIZER: AdamW + Cosine
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        
        {/* Card 1: Current Epoch */}
        <div className="glass-panel p-5 rounded-2xl border border-border hover:border-purple-500/40 relative overflow-hidden group transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
          <div className="absolute top-0 right-0 w-28 h-28 bg-purple-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-purple-500/20 transition-all" />
          
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-widest text-text-muted font-mono flex items-center gap-2">
              <RefreshCw size={15} className="text-purple-400 animate-spin" style={{ animationDuration: '8s' }} /> CURRENT EPOCH
            </span>
            <span className="text-[10px] font-mono bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30">96.0%</span>
          </div>

          <div className="my-3 flex items-baseline justify-between">
            <div>
              <span className="text-3xl font-black text-text-primary font-mono tracking-tight">48</span>
              <span className="text-lg font-bold text-text-muted font-mono ml-1">/ 50</span>
            </div>
            <span className="text-xs text-purple-400 font-bold font-mono">Phase 3 Final</span>
          </div>

          <div className="w-full bg-background-secondary h-2.5 rounded-full overflow-hidden border border-border p-0.5">
            <div 
              className="bg-gradient-to-r from-purple-600 via-indigo-500 to-cyan-400 h-full rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(168,85,247,0.5)]"
              style={{ width: '96%' }}
            />
          </div>
          <p className="text-[11px] text-text-muted mt-2.5 font-mono flex items-center justify-between">
            <span>Batch step: 1,420 / 1,480</span>
            <strong className="text-text-primary">Optimal convergence</strong>
          </p>
        </div>

        {/* Card 2: Remaining Time */}
        <div className="glass-panel p-5 rounded-2xl border border-border hover:border-cyan-500/40 relative overflow-hidden group transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
          <div className="absolute top-0 right-0 w-28 h-28 bg-cyan-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-cyan-500/20 transition-all" />
          
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-widest text-text-muted font-mono flex items-center gap-2">
              <Clock size={15} className="text-cyan-400" /> REMAINING TIME
            </span>
            <span className="text-[10px] font-mono bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/30">ETA</span>
          </div>

          <div className="my-3 flex items-baseline justify-between">
            <span className="text-3xl font-black text-text-primary font-mono tracking-tight">04:12</span>
            <span className="text-xs font-bold font-mono text-cyan-400">mins left</span>
          </div>

          <div className="w-full bg-background-secondary h-2.5 rounded-full overflow-hidden border border-border p-0.5">
            <div 
              className="bg-gradient-to-r from-cyan-500 to-teal-400 h-full rounded-full transition-all duration-500"
              style={{ width: '88%' }}
            />
          </div>
          <p className="text-[11px] text-text-muted mt-2.5 font-mono flex items-center justify-between">
            <span>Throughput:</span>
            <strong className="text-cyan-300">14.8 batches / sec</strong>
          </p>
        </div>

        {/* Card 3: GPU Usage */}
        <div className="glass-panel p-5 rounded-2xl border border-border hover:border-amber-500/40 relative overflow-hidden group transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
          <div className="absolute top-0 right-0 w-28 h-28 bg-amber-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-amber-500/20 transition-all" />
          
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-widest text-text-muted font-mono flex items-center gap-2">
              <Flame size={15} className="text-amber-400" /> GPU USAGE
            </span>
            <span className="text-[10px] font-mono bg-red-500/20 text-red-300 font-bold px-2 py-0.5 rounded border border-red-500/30">78°C / COOL</span>
          </div>

          <div className="my-3 flex items-baseline justify-between">
            <span className="text-2xl font-black text-text-primary font-mono tracking-tight truncate">RTX 4090</span>
            <span className="text-xl font-bold font-mono text-amber-400">84%</span>
          </div>

          <div className="w-full bg-background-secondary h-2.5 rounded-full overflow-hidden border border-border p-0.5">
            <div 
              className="bg-gradient-to-r from-amber-500 to-red-500 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_rgba(245,158,11,0.4)]"
              style={{ width: '84%' }}
            />
          </div>
          <p className="text-[11px] text-text-muted mt-2.5 font-mono flex items-center justify-between">
            <span>CUDA Cores:</span>
            <strong className="text-amber-300">16,384 Active</strong>
          </p>
        </div>

        {/* Card 4: Memory Usage */}
        <div className="glass-panel p-5 rounded-2xl border border-border hover:border-emerald-500/40 relative overflow-hidden group transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
          <div className="absolute top-0 right-0 w-28 h-28 bg-emerald-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-emerald-500/20 transition-all" />
          
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-widest text-text-muted font-mono flex items-center gap-2">
              <HardDrive size={15} className="text-emerald-400" /> MEMORY USAGE
            </span>
            <span className="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30">76.6% VRAM</span>
          </div>

          <div className="my-3 flex items-baseline justify-between">
            <span className="text-3xl font-black text-text-primary font-mono tracking-tight">18.4</span>
            <span className="text-sm font-bold font-mono text-text-muted">/ 24.0 GB</span>
          </div>

          <div className="w-full bg-background-secondary h-2.5 rounded-full overflow-hidden border border-border p-0.5">
            <div 
              className="bg-gradient-to-r from-emerald-500 via-teal-400 to-cyan-400 h-full rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(16,185,129,0.4)]"
              style={{ width: '76.6%' }}
            />
          </div>
          <p className="text-[11px] text-text-muted mt-2.5 font-mono flex items-center justify-between">
            <span>System Host RAM:</span>
            <strong className="text-emerald-300">32.8 / 64 GB</strong>
          </p>
        </div>

        {/* Card 5: Learning Rate */}
        <div className="glass-panel p-5 rounded-2xl border border-border hover:border-pink-500/40 relative overflow-hidden group transition-all duration-300 shadow-[0_4px_20px_rgba(0,0,0,0.4)]">
          <div className="absolute top-0 right-0 w-28 h-28 bg-pink-500/10 rounded-full blur-2xl pointer-events-none group-hover:bg-pink-500/20 transition-all" />
          
          <div className="flex items-center justify-between">
            <span className="text-xs font-black uppercase tracking-widest text-text-muted font-mono flex items-center gap-2">
              <Sparkles size={15} className="text-pink-400" /> LEARNING RATE
            </span>
            <span className="text-[10px] font-mono bg-pink-500/20 text-pink-300 px-2 py-0.5 rounded border border-pink-500/30">DECAY</span>
          </div>

          <div className="my-3 flex items-baseline justify-between">
            <span className="text-3xl font-black text-text-primary font-mono tracking-tight">1.5e-4</span>
            <span className="text-xs font-bold font-mono text-pink-400">Cosine</span>
          </div>

          <div className="w-full bg-background-secondary h-2.5 rounded-full overflow-hidden border border-border p-0.5">
            <div 
              className="bg-gradient-to-r from-pink-500 to-purple-500 h-full rounded-full transition-all duration-500 shadow-[0_0_8px_rgba(236,72,153,0.4)]"
              style={{ width: '35%' }}
            />
          </div>
          <p className="text-[11px] text-text-muted mt-2.5 font-mono flex items-center justify-between">
            <span>Warmup: Completed</span>
            <strong className="text-pink-300">&eta; min: 1.0e-6</strong>
          </p>
        </div>

      </div>
    </div>
  );
};
