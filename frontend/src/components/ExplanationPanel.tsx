import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, BrainCircuit, Activity, FileText, AlertTriangle } from 'lucide-react';
import { ConnectedDevice } from '../hooks/useNetworkData';

interface ExplanationPanelProps {
  isOpen: boolean;
  onClose: () => void;
  device: ConnectedDevice | null;
}

export const ExplanationPanel: React.FC<ExplanationPanelProps> = ({ isOpen, onClose, device }) => {
  if (!device || !device.ai_explanation) return null;
  const { message, reasoning, evidence, confidence, root_cause } = device.ai_explanation;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ x: '100%' }}
          animate={{ x: 0 }}
          exit={{ x: '100%' }}
          transition={{ type: 'spring', damping: 25, stiffness: 200 }}
          className="fixed top-0 right-0 w-96 h-screen bg-[#0a0f1d] border-l border-border shadow-2xl z-50 flex flex-col"
        >
          <div className="flex items-center justify-between p-4 border-b border-border bg-background-secondary/50">
            <h2 className="text-lg font-bold text-text-primary tracking-widest flex items-center gap-2">
              <BrainCircuit className="text-purple-500" /> AI EXPLANATION
            </h2>
            <button onClick={onClose} className="text-text-muted hover:text-text-primary transition-colors">
              <X size={20} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
            
            <div className="bg-purple-900/20 border border-purple-500/30 p-4 rounded-xl">
              <h3 className="text-purple-400 font-bold uppercase text-xs mb-2 tracking-wider">Analysis Result</h3>
              <p className="text-text-primary leading-relaxed font-medium">{message}</p>
            </div>

            <div className="space-y-4">
              <div className="flex items-start gap-3">
                <FileText className="text-blue-400 mt-0.5 shrink-0" size={18} />
                <div>
                  <h4 className="text-blue-400 font-bold uppercase text-xs mb-1 tracking-wider">Reasoning</h4>
                  <p className="text-text-primary text-sm leading-relaxed">{reasoning}</p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <Activity className="text-green-400 mt-0.5 shrink-0" size={18} />
                <div>
                  <h4 className="text-green-400 font-bold uppercase text-xs mb-1 tracking-wider">Evidence</h4>
                  <p className="text-text-primary text-sm leading-relaxed">{evidence}</p>
                </div>
              </div>
            </div>

            {root_cause && (
              <div className="mt-8 border border-orange-500/30 bg-orange-950/20 rounded-xl p-4">
                <h3 className="text-orange-400 font-bold uppercase text-xs mb-3 tracking-wider flex items-center gap-2">
                  <AlertTriangle size={16} /> Root Cause Analysis
                </h3>
                <div className="space-y-3">
                  <div>
                    <span className="text-text-muted text-xs font-bold">POSSIBLE CAUSES:</span>
                    <ul className="list-disc list-inside text-text-primary text-sm mt-1">
                      {root_cause.possible_causes.map((c: string, i: number) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                  <div>
                    <span className="text-text-muted text-xs font-bold">IMPACT:</span>
                    <p className="text-text-primary text-sm mt-1">{root_cause.impact}</p>
                  </div>
                  <div>
                    <span className="text-text-muted text-xs font-bold">SUGGESTED ACTIONS:</span>
                    <ul className="list-disc list-inside text-blue-300 text-sm mt-1">
                      {root_cause.actions.map((c: string, i: number) => <li key={i}>{c}</li>)}
                    </ul>
                  </div>
                </div>
              </div>
            )}

          </div>
          
          <div className="p-4 border-t border-border bg-background-secondary/50 flex justify-between items-center">
            <span className="text-text-muted text-xs font-mono">Confidence Level</span>
            <div className="flex items-center gap-2">
              <div className="w-24 h-1.5 bg-card rounded-full overflow-hidden">
                <div 
                  className="h-full bg-blue-500 transition-all duration-1000" 
                  style={{ width: `${confidence}%` }}
                />
              </div>
              <span className="text-blue-400 font-bold font-mono text-sm">{confidence}%</span>
            </div>
          </div>

        </motion.div>
      )}
    </AnimatePresence>
  );
};
