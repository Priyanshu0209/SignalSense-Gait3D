import React, { useState } from 'react';
import { NetworkEvent } from '../hooks/useNetworkData';
import { AlertCircle, CheckCircle2, Info, AlertTriangle, Activity, Navigation } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface TimelineProps {
  events: NetworkEvent[];
}

type EventFilter = 'all' | 'info' | 'success' | 'warning' | 'error';

export const Timeline: React.FC<TimelineProps> = ({ events }) => {
  const [filter, setFilter] = useState<EventFilter>('all');

  const filteredEvents = events.filter(e => filter === 'all' || e.type === filter);

  return (
    <div className="glass-panel p-5 h-full flex flex-col relative overflow-hidden">
      <div className="absolute top-0 right-0 w-32 h-32 bg-blue-500/10 blur-3xl rounded-full pointer-events-none" />
      
      <div className="flex justify-between items-center mb-5 z-10">
        <h3 className="text-sm font-bold text-text-primary tracking-[0.2em] px-2 flex items-center gap-2">
          <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse" />
          SOC LOG
        </h3>
        
        <div className="flex gap-1 bg-card p-1 rounded-lg border border-border">
          <FilterButton current={filter} value="all" label="ALL" onClick={setFilter} />
          <FilterButton current={filter} value="warning" label="WARN" onClick={setFilter} />
          <FilterButton current={filter} value="error" label="ERR" onClick={setFilter} />
        </div>
      </div>

      <div className="flex-grow overflow-y-auto custom-scrollbar px-2 space-y-4 relative z-10">
        <div className="absolute left-[21px] top-0 bottom-0 w-px bg-gradient-to-b from-blue-500/50 via-slate-800 to-transparent pointer-events-none" />
        
        <AnimatePresence>
          {filteredEvents.length === 0 ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center text-text-muted text-xs mt-10 font-mono">
              WAITING FOR TELEMETRY...
            </motion.div>
          ) : (
            filteredEvents.map((event, index) => (
              <motion.div
                key={event.id}
                initial={{ opacity: 0, x: -20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: index * 0.02 }}
                className="relative pl-12 group"
              >
                <div className="absolute left-[9px] top-1.5 z-20 transition-transform group-hover:scale-125">
                  {getEventIcon(event.type, event.message)}
                </div>
                <div className="bg-card rounded-xl p-3 border border-border group-hover:border-blue-500/30 transition-colors relative overflow-hidden">
                  <div className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-blue-500/50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                  <div className="flex justify-between items-start mb-1">
                    <p className={`text-[10px] font-bold uppercase tracking-wider ${getTextColor(event.type)}`}>
                      {event.type}
                    </p>
                    <p className="text-[10px] text-text-muted font-mono">
                      {new Date(event.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute:'2-digit', second:'2-digit' })}
                    </p>
                  </div>
                  <p className="text-sm text-text-primary leading-snug">{event.message}</p>
                </div>
              </motion.div>
            ))
          )}
        </AnimatePresence>
      </div>
    </div>
  );
};

const FilterButton = ({ current, value, label, onClick }: { current: string, value: EventFilter, label: string, onClick: (f: EventFilter) => void }) => {
  const active = current === value;
  return (
    <button
      onClick={() => onClick(value)}
      className={`px-2 py-1 text-[9px] font-bold tracking-wider rounded ${
        active ? 'bg-blue-600 text-text-primary' : 'text-text-muted hover:bg-foreground/10'
      } transition-colors`}
    >
      {label}
    </button>
  );
};

const getEventIcon = (type: NetworkEvent['type'], message: string) => {
  const msg = message.toLowerCase();
  
  if (msg.includes('spike') || msg.includes('traffic')) {
    return <div className="w-6 h-6 rounded-full bg-purple-900/50 flex items-center justify-center border border-purple-500/50 shadow-[0_0_10px_rgba(168,85,247,0.4)]"><Activity size={12} className="text-purple-400"/></div>;
  }
  if (msg.includes('move') || msg.includes('drift')) {
    return <div className="w-6 h-6 rounded-full bg-cyan-900/50 flex items-center justify-center border border-cyan-500/50 shadow-[0_0_10px_rgba(6,182,212,0.4)]"><Navigation size={12} className="text-cyan-400"/></div>;
  }

  switch (type) {
    case 'info': return <div className="w-6 h-6 rounded-full bg-blue-900/80 flex items-center justify-center border border-blue-500/80 shadow-[0_0_10px_rgba(59,130,246,0.4)]"><Info size={12} className="text-blue-400"/></div>;
    case 'success': return <div className="w-6 h-6 rounded-full bg-green-900/80 flex items-center justify-center border border-green-500/80 shadow-[0_0_10px_rgba(34,197,94,0.4)]"><CheckCircle2 size={12} className="text-green-400"/></div>;
    case 'warning': return <div className="w-6 h-6 rounded-full bg-yellow-900/80 flex items-center justify-center border border-yellow-500/80 shadow-[0_0_10px_rgba(234,179,8,0.4)]"><AlertTriangle size={12} className="text-yellow-400"/></div>;
    case 'error': return <div className="w-6 h-6 rounded-full bg-red-900/80 flex items-center justify-center border border-red-500/80 shadow-[0_0_10px_rgba(239,68,68,0.4)]"><AlertCircle size={12} className="text-red-400"/></div>;
  }
};

const getTextColor = (type: NetworkEvent['type']) => {
  switch (type) {
    case 'info': return 'text-blue-400';
    case 'success': return 'text-green-400';
    case 'warning': return 'text-yellow-400';
    case 'error': return 'text-red-400';
  }
};
