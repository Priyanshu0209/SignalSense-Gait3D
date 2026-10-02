import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';

interface AICopilotProps {
  isOpen: boolean;
  onClose: () => void;
}

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  confidence?: number;
}

export const AICopilot: React.FC<AICopilotProps> = ({ isOpen, onClose }) => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { id: '1', text: 'Hello! I am your AI Copilot. Ask me about network health, bandwidth hogs, or predict future load.', sender: 'bot', confidence: 100 }
  ]);
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (bottomRef.current) {
      bottomRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMsg: Message = { id: Date.now().toString(), text: query, sender: 'user' };
    setMessages(prev => [...prev, userMsg]);
    setQuery('');
    setLoading(true);

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
      const res = await fetch(`${API_URL}/analytics/copilot`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: userMsg.text })
      });
      
      const data = await res.json();
      
      const botMsg: Message = { 
        id: (Date.now() + 1).toString(), 
        text: data.answer, 
        sender: 'bot',
        confidence: data.confidence
      };
      
      setMessages(prev => [...prev, botMsg]);
    } catch (error) {
      setMessages(prev => [...prev, { id: Date.now().toString(), text: 'Error connecting to the Copilot Engine.', sender: 'bot', confidence: 0 }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-24 right-8 w-96 h-[500px] bg-background-secondary/90 border border-border shadow-2xl rounded-2xl flex flex-col z-50 backdrop-blur-xl overflow-hidden">
      <div className="p-4 border-b border-border bg-card flex justify-between items-center">
        <h3 className="text-text-primary font-bold tracking-widest flex items-center gap-2 text-sm">
          <Sparkles className="text-blue-400" size={16} /> AI COPILOT
        </h3>
        <button onClick={onClose} className="text-text-muted hover:text-text-primary">&times;</button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {messages.map(m => (
          <div key={m.id} className={`flex flex-col ${m.sender === 'user' ? 'items-end' : 'items-start'}`}>
            <div className={`max-w-[85%] rounded-2xl p-3 text-sm ${m.sender === 'user' ? 'bg-blue-600 text-text-primary' : 'bg-card text-text-primary border border-border'}`}>
              <div className="flex items-center gap-2 mb-1 opacity-60">
                {m.sender === 'user' ? <User size={12}/> : <Bot size={12}/>}
                <span className="text-[10px] uppercase font-bold">{m.sender}</span>
              </div>
              <p>{m.text}</p>
            </div>
            {m.sender === 'bot' && m.confidence !== undefined && (
              <span className="text-[10px] text-text-muted mt-1 ml-1 font-mono">
                Confidence: {m.confidence.toFixed(1)}%
              </span>
            )}
          </div>
        ))}
        {loading && (
          <div className="flex items-start">
            <div className="bg-card rounded-2xl p-3 border border-border text-text-muted text-sm animate-pulse flex items-center gap-2">
              <Bot size={14}/> Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSubmit} className="p-3 border-t border-border bg-card flex gap-2">
        <input 
          type="text" 
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask a question..."
          className="flex-1 bg-card border border-border rounded-xl px-4 py-2 text-sm text-text-primary focus:outline-none focus:border-blue-500 transition-colors"
        />
        <button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-500 text-text-primary p-2 rounded-xl transition-colors flex items-center justify-center">
          <Send size={18} />
        </button>
      </form>
    </div>
  );
};
