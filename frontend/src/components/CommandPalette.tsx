import React, { useEffect, useState } from 'react';
import { Search, Terminal, Navigation, ShieldAlert } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface CommandPaletteProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigate: (view: 'radar' | 'topology' | 'analytics') => void;
  onSearch: (query: string) => void;
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose, onNavigate, onSearch }) => {
  const [query, setQuery] = useState('');

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        isOpen ? onClose() : document.dispatchEvent(new CustomEvent('open-command-palette'));
      }
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  useEffect(() => {
    // Live Semantic parsing
    if (query.toLowerCase().includes('unstable')) {
      onSearch('unstable');
    } else if (query.toLowerCase().includes('stream')) {
      onSearch('streaming');
    } else if (query.toLowerCase().includes('iot')) {
      onSearch('iot');
    } else if (query.toLowerCase().includes('offline')) {
      onSearch('offline');
    } else if (query.trim() === '') {
      onSearch('');
    } else {
      onSearch(query);
    }
  }, [query, onSearch]);

  if (!isOpen) return null;

  const runCommand = (action: () => void) => {
    action();
    onClose();
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[100] bg-card backdrop-blur-sm flex items-start justify-center pt-[15vh]"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, y: -20, opacity: 0 }}
          animate={{ scale: 1, y: 0, opacity: 1 }}
          exit={{ scale: 0.95, y: -20, opacity: 0 }}
          transition={{ type: 'spring', damping: 25, stiffness: 300 }}
          className="w-full max-w-2xl bg-background-secondary border border-border rounded-2xl shadow-2xl overflow-hidden"
          onClick={e => e.stopPropagation()}
        >
          <div className="flex items-center px-4 py-3 border-b border-border bg-background-secondary/50">
            <Terminal size={20} className="text-blue-500 mr-3" />
            <input
              type="text"
              autoFocus
              placeholder="Type a command or search..."
              value={query}
              onChange={e => setQuery(e.target.value)}
              className="flex-1 bg-transparent border-none outline-none text-text-primary placeholder-slate-500 text-lg font-mono"
            />
            <div className="flex gap-2">
              <kbd className="px-2 py-1 bg-card rounded text-xs text-text-muted font-mono">ESC</kbd>
            </div>
          </div>

          <div className="max-h-96 overflow-y-auto custom-scrollbar p-2">
            <div className="px-3 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider">
              Views
            </div>
            <CommandItem
              icon={<Navigation size={16} className="text-blue-400" />}
              label="Switch to Radar View"
              shortcut="G R"
              onClick={() => runCommand(() => onNavigate('radar'))}
            />
            <CommandItem
              icon={<Search size={16} className="text-green-400" />}
              label="Switch to Topology Graph"
              shortcut="G T"
              onClick={() => runCommand(() => onNavigate('topology'))}
            />
            <CommandItem
              icon={<ShieldAlert size={16} className="text-purple-400" />}
              label="Switch to Analytics"
              shortcut="G A"
              onClick={() => runCommand(() => onNavigate('analytics'))}
            />
            
            <div className="px-3 py-2 text-xs font-semibold text-text-muted uppercase tracking-wider mt-4">
              Actions
            </div>
            <CommandItem
              icon={<Terminal size={16} className="text-text-muted" />}
              label="Run Network Diagnostics"
              shortcut="CMD D"
              onClick={() => runCommand(() => console.log('Run Diagnostics'))}
            />
            <CommandItem
              icon={<Search size={16} className="text-text-muted" />}
              label="Export PDF Report"
              onClick={() => runCommand(() => console.log('Export PDF'))}
            />
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

const CommandItem = ({ icon, label, shortcut, onClick }: { icon: React.ReactNode, label: string, shortcut?: string, onClick: () => void }) => (
  <button
    onClick={onClick}
    className="w-full flex items-center justify-between px-3 py-3 rounded-xl hover:bg-blue-600/20 text-left transition-colors group"
  >
    <div className="flex items-center gap-3">
      <div className="p-1.5 rounded-lg bg-card group-hover:bg-blue-500/20 transition-colors">
        {icon}
      </div>
      <span className="text-text-primary group-hover:text-blue-100 font-medium">{label}</span>
    </div>
    {shortcut && (
      <span className="text-xs text-text-muted font-mono group-hover:text-blue-300 tracking-widest">{shortcut}</span>
    )}
  </button>
);
