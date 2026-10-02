import React, { useRef, useState, useEffect } from 'react';
import { ConnectedDevice } from '../hooks/useNetworkData';
import { GroundTruth } from '../hooks/useDatasetCollection';
import { Router } from 'lucide-react';

interface Props {
  devices: ConnectedDevice[];
  groundTruths: Record<string, GroundTruth>;
  onUpdate: (gt: GroundTruth) => void;
  disabled: boolean;
}

export const PolarMap: React.FC<Props> = ({ devices, groundTruths, onUpdate, disabled }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState(400);
  const [draggingMac, setDraggingMac] = useState<string | null>(null);

  // Auto-resize
  useEffect(() => {
    if (!containerRef.current) return;
    const observer = new ResizeObserver(entries => {
      for (let entry of entries) {
        const { width, height } = entry.contentRect;
        setSize(Math.min(width, height) - 40); // 20px padding
      }
    });
    observer.observe(containerRef.current);
    return () => observer.disconnect();
  }, []);

  const MAX_DISTANCE = 15; // Assume 15 meters is max scale for the map view
  const radius = size / 2;
  const center = { x: radius, y: radius };

  const getCoordinates = (distance: number, direction: number) => {
    const r = (Math.min(distance, MAX_DISTANCE) / MAX_DISTANCE) * radius;
    // direction is 0-359. Standard polar: 0 is right. We want 0 to be top.
    // In SVG, Y is down. So 0° = top (x: 0, y: -r), 90° = right (x: r, y: 0)
    const angleRad = (direction - 90) * (Math.PI / 180);
    return {
      x: center.x + r * Math.cos(angleRad),
      y: center.y + r * Math.sin(angleRad)
    };
  };

  const getDistanceAndDirection = (x: number, y: number) => {
    const dx = x - center.x;
    const dy = y - center.y;
    const r = Math.sqrt(dx*dx + dy*dy);
    const distance = (r / radius) * MAX_DISTANCE;
    
    // angle in radians from positive X axis
    let angleRad = Math.atan2(dy, dx);
    let direction = (angleRad * (180 / Math.PI)) + 90;
    if (direction < 0) direction += 360;
    
    return {
      distance: Math.max(0, parseFloat(distance.toFixed(2))),
      direction: Math.round(direction)
    };
  };

  const handlePointerDown = (mac: string, e: React.PointerEvent) => {
    if (disabled) return;
    if (e.target instanceof Element) e.target.setPointerCapture(e.pointerId);
    setDraggingMac(mac);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!draggingMac || disabled) return;
    
    const svg = e.currentTarget as SVGSVGElement;
    const pt = svg.createSVGPoint();
    pt.x = e.clientX;
    pt.y = e.clientY;
    const cursorPt = pt.matrixTransform(svg.getScreenCTM()?.inverse());
    
    const { distance, direction } = getDistanceAndDirection(cursorPt.x, cursorPt.y);
    const gt = groundTruths[draggingMac];
    if (gt) {
      onUpdate({ ...gt, distance, direction });
    }
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    if (draggingMac) {
      if (e.target instanceof Element) e.target.releasePointerCapture(e.pointerId);
      setDraggingMac(null);
    }
  };

  // Color palette for devices
  const colors = ['#ef4444', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899', '#14b8a6'];

  return (
    <div ref={containerRef} className="w-full h-full flex items-center justify-center relative touch-none">
      <svg 
        width={size} 
        height={size} 
        className="overflow-visible"
        onPointerMove={handlePointerMove}
        onPointerUp={handlePointerUp}
        onPointerLeave={handlePointerUp}
      >
        {/* Grid Circles */}
        {[0.25, 0.5, 0.75, 1.0].map(pct => (
          <circle key={pct} cx={center.x} cy={center.y} r={radius * pct} fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="1" strokeDasharray="4 4" />
        ))}
        {/* Crosshairs */}
        <line x1={center.x} y1={0} x2={center.x} y2={size} stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
        <line x1={0} y1={center.y} x2={size} y2={center.y} stroke="rgba(255,255,255,0.1)" strokeWidth="1" />
        
        {/* Router at Center */}
        <g transform={`translate(${center.x - 16}, ${center.y - 16})`}>
          <rect width="32" height="32" rx="8" fill="rgba(30,41,59,0.8)" stroke="#3b82f6" strokeWidth="2" />
          <Router size={20} x="6" y="6" className="text-blue-400" />
        </g>

        {/* Devices */}
        {devices.map((device, index) => {
          const gt = groundTruths[device.mac_address];
          if (!gt || !gt.include_in_collection) return null;
          
          const coords = getCoordinates(gt.distance, gt.direction);
          const color = colors[index % colors.length];
          const isDragging = draggingMac === device.mac_address;
          
          return (
            <g key={device.mac_address} 
               transform={`translate(${coords.x}, ${coords.y})`}
               className={disabled ? 'cursor-not-allowed' : 'cursor-pointer'}
               onPointerDown={(e) => handlePointerDown(device.mac_address, e)}
            >
              {/* Distance Line */}
              <line x1={center.x - coords.x} y1={center.y - coords.y} x2={0} y2={0} stroke={color} strokeWidth="1" strokeDasharray="2 4" opacity="0.5" />
              
              <circle r={isDragging ? 12 : 8} fill={color} className="transition-all duration-200 shadow-[0_0_10px_currentColor]" />
              <text y="-16" textAnchor="middle" fill="white" fontSize="10" className="font-bold pointer-events-none drop-shadow-md">
                {device.hostname || 'Unknown'}
              </text>
              <text y="18" textAnchor="middle" fill="rgba(255,255,255,0.7)" fontSize="9" className="font-mono pointer-events-none">
                {gt.distance.toFixed(1)}m, {gt.direction}°
              </text>
            </g>
          );
        })}
      </svg>
      {/* Legend / Axis Labels */}
      <div className="absolute top-2 left-1/2 -translate-x-1/2 text-xs font-mono text-text-muted">0°</div>
      <div className="absolute bottom-2 left-1/2 -translate-x-1/2 text-xs font-mono text-text-muted">180°</div>
      <div className="absolute right-2 top-1/2 -translate-y-1/2 text-xs font-mono text-text-muted">90°</div>
      <div className="absolute left-2 top-1/2 -translate-y-1/2 text-xs font-mono text-text-muted">270°</div>
    </div>
  );
};
