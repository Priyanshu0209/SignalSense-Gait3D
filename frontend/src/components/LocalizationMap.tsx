import React, { useRef, useState, useEffect } from 'react';
import { Router } from 'lucide-react';
import { ReplayFrame } from '../hooks/useLocalization';

interface Props {
  frame: ReplayFrame | null;
}

export const LocalizationMap: React.FC<Props> = ({ frame }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState(400);

  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        setSize(Math.min(width, height) - 40);
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const MAX_DISTANCE = 15;
  const radius = size / 2;
  const center = { x: radius, y: radius };

  const getCoordinates = (distance: number, direction: number) => {
    const r = (Math.min(distance, MAX_DISTANCE) / MAX_DISTANCE) * radius;
    const angleRad = (direction - 90) * (Math.PI / 180);
    return {
      x: center.x + r * Math.cos(angleRad),
      y: center.y + r * Math.sin(angleRad)
    };
  };

  return (
    <div ref={containerRef} className="w-full h-full flex items-center justify-center relative bg-[#020617]">
      <svg width={size} height={size} className="overflow-visible">
        {/* Grid Circles */}
        {[0.25, 0.5, 0.75, 1.0].map(pct => (
          <circle key={pct} cx={center.x} cy={center.y} r={radius * pct} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="1" strokeDasharray="4 4" />
        ))}
        {/* Crosshairs */}
        <line x1={center.x} y1={0} x2={center.x} y2={size} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        <line x1={0} y1={center.y} x2={size} y2={center.y} stroke="rgba(255,255,255,0.05)" strokeWidth="1" />
        
        {/* Router at Center */}
        <g transform={`translate(${center.x - 16}, ${center.y - 16})`}>
          <rect width="32" height="32" rx="8" fill="rgba(30,41,59,0.8)" stroke="#3b82f6" strokeWidth="2" />
          <Router size={20} x="6" y="6" className="text-blue-400" />
        </g>

        {frame && (
          <g>
            {/* Ground Truth Point */}
            <g transform={`translate(${getCoordinates(frame.gt_distance, frame.gt_direction).x}, ${getCoordinates(frame.gt_distance, frame.gt_direction).y})`}>
              <circle r="6" fill="#10b981" />
              <text y="-12" textAnchor="middle" fill="#10b981" fontSize="10" className="font-bold">GT</text>
            </g>

            {/* AI Prediction Point */}
            <g transform={`translate(${getCoordinates(frame.est_distance, frame.est_direction).x}, ${getCoordinates(frame.est_distance, frame.est_direction).y})`}>
              <circle r="6" fill="#ef4444" className="animate-pulse" />
              <text y="20" textAnchor="middle" fill="#ef4444" fontSize="10" className="font-bold">AI</text>
            </g>

            {/* Error Vector Line */}
            <line 
              x1={getCoordinates(frame.gt_distance, frame.gt_direction).x} 
              y1={getCoordinates(frame.gt_distance, frame.gt_direction).y} 
              x2={getCoordinates(frame.est_distance, frame.est_direction).x} 
              y2={getCoordinates(frame.est_distance, frame.est_direction).y} 
              stroke="#f59e0b" 
              strokeWidth="2" 
              strokeDasharray="4 4"
            />
          </g>
        )}
      </svg>
      {/* Legend / Axis Labels */}
      <div className="absolute top-2 left-1/2 -translate-x-1/2 text-xs font-mono text-text-muted">0°</div>
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-mono text-text-muted">180°</div>
      <div className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-mono text-text-muted">90°</div>
      <div className="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-mono text-text-muted">270°</div>
    </div>
  );
};
