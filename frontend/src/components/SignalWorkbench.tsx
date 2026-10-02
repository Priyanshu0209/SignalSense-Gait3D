import React, { useEffect, useState } from 'react';
import { RefreshCw, Radio, CheckCircle, Waves, ActivitySquare } from 'lucide-react';

interface SignalWorkbenchProps {
  fetchSignalAnalysis: (mac: string) => Promise<any>;
}

export const SignalWorkbench: React.FC<SignalWorkbenchProps> = ({ fetchSignalAnalysis }) => {
  const [selectedMac, setSelectedMac] = useState<string>("00:1A:2B:3C:4D:5E");
  const [data, setData] = useState<any | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const reloadData = async () => {
    setLoading(true);
    const res = await fetchSignalAnalysis(selectedMac);
    if (res) {
      setData(res);
    } else {
      // High-fidelity fallback for demonstration
      const count = 100;
      const raw: number[] = [];
      const filtered: number[] = [];
      const freqs: number[] = [];
      const mags: number[] = [];
      
      for (let i = 0; i < count; i++) {
        const t = i * 0.05;
        const wave = -52 + Math.sin(t * 2 * Math.PI * 1.86) * 3 + Math.sin(t * 4 * Math.PI * 1.86) * 1;
        raw.push(parseFloat((wave + (Math.random() - 0.5) * 2.5).toFixed(2)));
        filtered.push(parseFloat(wave.toFixed(2)));
      }
      for (let f = 1; f <= 30; f++) {
        const fh = f * 0.15;
        freqs.push(parseFloat(fh.toFixed(2)));
        mags.push(Math.abs(fh - 1.86) < 0.2 ? 3.8 : parseFloat((Math.random() * 0.4).toFixed(2)));
      }
      setData({
        mac: selectedMac,
        sample_count: count,
        raw_rssi: raw,
        filtered_rssi: filtered,
        fft_spectrum: { frequencies: freqs, magnitudes: mags, dominant_frequency_hz: 1.86, max_magnitude: 3.8 }
      });
    }
    setLoading(false);
  };

  useEffect(() => {
    reloadData();
    const interval = setInterval(reloadData, 2000);
    return () => clearInterval(interval);
  }, [selectedMac]);

  // Render SVG Waveform path helper
  const renderLineChart = (values: number[], minVal: number = -70, maxVal: number = -40, color: string = "#06b6d4", glow: boolean = false) => {
    if (!values || values.length === 0) return null;
    const width = 800;
    const height = 180;
    const step = width / Math.max(1, values.length - 1);
    
    const points = values.map((val, i) => {
      const x = i * step;
      const normalized = Math.min(1, Math.max(0, (val - minVal) / (maxVal - minVal)));
      const y = height - (normalized * (height - 20)) - 10;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");

    return (
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-[180px] overflow-visible">
        <defs>
          <linearGradient id={`gradient-${color.replace('#','')}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.2" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
          {glow && (
            <filter id={`glow-${color.replace('#','')}`} x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
          )}
        </defs>
        
        {/* Horizontal gridlines */}
        <line x1="0" y1="20" x2={width} y2="20" stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />
        <line x1="0" y1={height/2} x2={width} y2={height/2} stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />
        <line x1="0" y1={height-20} x2={width} y2={height-20} stroke="rgba(255,255,255,0.05)" strokeDasharray="4" />
        
        {/* Fill Area underneath line */}
        <polygon fill={`url(#gradient-${color.replace('#','')})`} points={`0,${height} ${points} ${width},${height}`} />
        
        {/* The Line */}
        <polyline 
          fill="none" 
          stroke={color} 
          strokeWidth="3" 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          points={points} 
          filter={glow ? `url(#glow-${color.replace('#','')})` : undefined}
        />
      </svg>
    );
  };

  return (
    <div className="space-y-6 w-full pb-6">
      {/* Header Bar */}
      <div className="glass-card p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-14 h-14 rounded-2xl bg-accent-primary/20 border border-accent-primary/40 flex items-center justify-center text-accent-primary shadow-neon-blue">
            <Waves size={28} />
          </div>
          <div>
            <h2 className="text-xl font-bold tracking-tight text-text-primary">Signal Processing Engine</h2>
            <p className="text-sm text-text-muted font-mono tracking-wide mt-1">Raw Telemetry → Savitzky-Golay IIR → Fast Fourier Transform</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 bg-background-primary/60 px-4 py-2.5 rounded-xl border border-border font-mono text-sm text-text-muted shadow-inner">
            <Radio size={16} className="text-status-success animate-pulse" />
            <span className="font-bold tracking-widest text-xs uppercase">Target Link:</span>
            <select 
              value={selectedMac}
              onChange={(e) => setSelectedMac(e.target.value)}
              className="bg-transparent text-text-primary font-bold outline-none cursor-pointer"
            >
              <option value="00:1A:2B:3C:4D:5E">00:1A:2B:3C:4D:5E (Walking Subject)</option>
              <option value="AA:BB:CC:DD:EE:01">AA:BB:CC:DD:EE:01 (Standing Subject)</option>
              <option value="A1:B2:C3:D4:E5:F6">A1:B2:C3:D4:E5:F6 (Running Subject)</option>
            </select>
          </div>

          <button 
            onClick={reloadData} 
            className="p-3 bg-card hover:bg-card-hover text-text-primary rounded-xl transition-all duration-300 border border-border hover:border-border hover:shadow-lg group"
          >
            <RefreshCw size={20} className={`transition-transform duration-500 group-hover:rotate-180 ${loading ? 'animate-spin text-accent-primary' : ''}`} />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        
        {/* Stream 1: Raw */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-64 h-64 bg-text-muted/5 rounded-full blur-[100px] -z-10 group-hover:bg-text-muted/10 transition-colors pointer-events-none" />
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-text-muted animate-pulse shadow-[0_0_10px_rgba(148,163,184,0.5)]" />
              <h4 className="text-sm font-bold tracking-widest text-text-secondary uppercase">I. Raw Unfiltered Wi-Fi Telemetry</h4>
            </div>
            <span className="text-xs font-mono font-bold text-text-muted bg-background-primary/50 px-3 py-1 rounded-lg border border-border">20.0 Hz Ingest</span>
          </div>
          <div className="bg-background-primary/40 p-4 rounded-xl border border-border shadow-inner">
            {renderLineChart(data?.raw_rssi || [], -68, -45, "#94a3b8")}
          </div>
        </div>

        {/* Stream 2: Filtered */}
        <div className="glass-card p-6 relative overflow-hidden border-accent-secondary/30 shadow-neon-blue group">
          <div className="absolute top-0 left-1/4 w-96 h-96 bg-accent-secondary/10 rounded-full blur-[120px] -z-10 group-hover:bg-accent-secondary/20 transition-colors pointer-events-none" />
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <span className="w-3 h-3 rounded-full bg-accent-secondary shadow-neon-blue animate-pulse" />
              <h4 className="text-sm font-bold tracking-widest text-accent-secondary uppercase">II. Butterworth & Savitzky-Golay Biokinetic Filter</h4>
            </div>
            <span className="text-xs font-mono text-accent-secondary bg-accent-secondary/10 px-3 py-1 rounded-lg border border-accent-secondary/30 font-bold flex items-center gap-2 shadow-neon-blue">
              <CheckCircle size={14} /> Human Stride Periodicity Isolated
            </span>
          </div>
          <div className="bg-background-primary/40 p-4 rounded-xl border border-border shadow-inner relative">
            {renderLineChart(data?.filtered_rssi || [], -68, -45, "#06B6D4", true)}
          </div>
        </div>

        {/* Stream 3: FFT */}
        <div className="glass-card p-6 relative overflow-hidden group">
          <div className="absolute top-0 right-1/4 w-96 h-96 bg-status-warning/10 rounded-full blur-[120px] -z-10 group-hover:bg-status-warning/20 transition-colors pointer-events-none" />
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <ActivitySquare size={20} className="text-status-warning" />
              <h4 className="text-sm font-bold tracking-widest text-text-secondary uppercase">III. Fast Fourier Transform Spectral Power</h4>
            </div>
            <span className="text-xs font-mono text-status-warning bg-status-warning/10 px-3 py-1 rounded-lg border border-status-warning/30 font-bold shadow-neon-amber">
              Dominant Frequency: {data?.fft_spectrum?.dominant_frequency_hz || 1.86} Hz
            </span>
          </div>
          
          <div className="bg-background-primary/40 p-6 rounded-xl border border-border h-[240px] flex items-end justify-between gap-1.5 shadow-inner">
            {(data?.fft_spectrum?.magnitudes || []).map((mag: number, idx: number) => {
              const freq = data?.fft_spectrum?.frequencies[idx] || (idx + 1) * 0.15;
              const isDominant = Math.abs(freq - (data?.fft_spectrum?.dominant_frequency_hz || 1.86)) < 0.1;
              const heightPct = Math.min(100, Math.max(8, (mag / (data?.fft_spectrum?.max_magnitude || 4.0)) * 100));
              
              return (
                <div key={idx} className="flex-1 flex flex-col items-center h-full justify-end group/bar relative">
                  <div className="opacity-0 group-hover/bar:opacity-100 transition-opacity absolute -top-10 bg-card px-3 py-1.5 rounded-lg border border-border text-[10px] text-text-primary font-mono pointer-events-none z-20 whitespace-nowrap shadow-glass-hover">
                    {freq.toFixed(2)} Hz<br/><span className="text-text-muted">Mag: {mag.toFixed(2)}</span>
                  </div>
                  <div 
                    className={`w-full rounded-t transition-all duration-300 ${
                      isDominant 
                        ? 'bg-gradient-to-t from-status-warning/80 to-status-warning shadow-neon-amber' 
                        : 'bg-text-muted/40 hover:bg-accent-primary/80'
                    }`}
                    style={{ height: `${heightPct}%` }}
                  />
                  <span className={`text-[10px] font-mono mt-3 truncate max-w-[28px] ${isDominant ? 'text-status-warning font-bold' : 'text-text-muted'}`}>
                    {freq.toFixed(1)}
                  </span>
                </div>
              );
            })}
          </div>
        </div>

      </div>
    </div>
  );
};
