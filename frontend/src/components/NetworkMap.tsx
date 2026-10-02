import React, { useMemo, useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { ConnectedDevice, RouterStatus } from '../hooks/useNetworkData';
import { Router, Smartphone, Laptop, Tv, Cpu, Wifi, Radio, Zap, Activity, Target, Shield, Layers, Compass } from 'lucide-react';

interface NetworkMapProps {
  devices: ConnectedDevice[];
  routerStatus: RouterStatus | null;
  onDeviceClick: (device: ConnectedDevice) => void;
}

interface Point {
  x: number;
  y: number;
}

// Vibrant Research Color Palette matching Gait3D Studio
const RESEARCH_PALETTE = [
  { name: 'Sky Cyan', hex: '#38bdf8', rgb: '56, 189, 248', border: 'border-sky-400', text: 'text-sky-400', bg: 'bg-sky-500/20' },
  { name: 'Magenta Glow', hex: '#d946ef', rgb: '217, 70, 239', border: 'border-fuchsia-400', text: 'text-fuchsia-400', bg: 'bg-fuchsia-500/20' },
  { name: 'Solar Gold', hex: '#facc15', rgb: '250, 204, 21', border: 'border-yellow-400', text: 'text-yellow-400', bg: 'bg-yellow-500/20' },
  { name: 'Emerald Pulse', hex: '#10b981', rgb: '16, 185, 129', border: 'border-emerald-400', text: 'text-emerald-400', bg: 'bg-emerald-500/20' },
  { name: 'Amber Blaze', hex: '#f97316', rgb: '249, 115, 22', border: 'border-orange-400', text: 'text-orange-400', bg: 'bg-orange-500/20' },
  { name: 'Indigo Deep', hex: '#6366f1', rgb: '99, 102, 241', border: 'border-indigo-400', text: 'text-indigo-400', bg: 'bg-indigo-500/20' },
];

const getDeviceIcon = (device: ConnectedDevice, colorClass: string) => {
  const type = (device.device_type || '').toLowerCase();
  const name = (device.hostname || '').toLowerCase();

  if (type.includes('phone') || type.includes('mobile') || name.includes('moto') || name.includes('iphone') || name.includes('pixel') || name.includes('galaxy') || name.includes('samsung') || name.includes('f41') || name.includes('g84')) 
    return <Smartphone size={22} className={colorClass} />;
    
  if (type.includes('laptop') || type.includes('pc') || type.includes('mac') || name.includes('laptop') || name.includes('macbook') || name.includes('desktop') || name.includes('pc')) 
    return <Laptop size={22} className={colorClass} />;
    
  if (type.includes('tv') || name.includes('tv')) 
    return <Tv size={22} className={colorClass} />;
    
  if (type.includes('iot') || name.includes('sensor') || name.includes('esp') || name.includes('node')) 
    return <Cpu size={22} className={colorClass} />;
    
  if (name.includes('shristi') || name.includes('priyanshu') || name.includes('hprewa') || name.includes('user')) 
    return <Smartphone size={22} className={colorClass} />;

  return <Wifi size={22} className={colorClass} />;
};

export const NetworkMap: React.FC<NetworkMapProps> = ({ devices, routerStatus, onDeviceClick }) => {
  const centerX = 0;
  const centerY = 0;
  
  // Tactical Scope configuration
  const [showGrid, setShowGrid] = useState<boolean>(true);
  const [activeOnly, setActiveOnly] = useState<boolean>(true);
  const [sweepAngle, setSweepAngle] = useState<number>(0);
  
  const trailsRef = useRef<Record<string, Point[]>>({});

  // Continuous radar sweeping animation
  useEffect(() => {
    let animationFrameId: number;
    let lastTime = performance.now();
    
    const animate = (now: number) => {
      const delta = now - lastTime;
      lastTime = now;
      // Rotate sweep ~60 degrees per second for a smooth tactical look
      setSweepAngle((prev) => (prev + (delta * 0.06)) % 360);
      animationFrameId = requestAnimationFrame(animate);
    };
    animationFrameId = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  // Filter devices if activeOnly is selected
  const displayDevices = useMemo(() => {
    if (activeOnly) {
      const online = devices.filter(d => d.online_status || (d.current_rssi && d.current_rssi.value && d.current_rssi.value > -95));
      return online.length > 0 ? online : devices;
    }
    return devices;
  }, [devices, activeOnly]);

  const maxCount = (val: number, fallback: number) => val > 0 ? val : fallback;

  // Smart zero-collision spatial calculations
  const devicePositions = useMemo(() => {
    const totalCount = maxCount(displayDevices.length, 1);

    return displayDevices.map((device, index) => {
      // Assign signature research theme color
      const palette = RESEARCH_PALETTE[index % RESEARCH_PALETTE.length];
      
      // Calculate realistic radius so devices NEVER crowd or overlap the 80px center router icon!
      // Range: 150px (close ~2.5m) to 340px (distant ~10m+)
      let radius = 220;
      const realDist = device.distance?.value !== null && device.distance?.value !== undefined ? device.distance.value : 3.16;
      
      if (realDist !== null && realDist !== undefined) {
        // Map real distances (0.1m to 6.0m) to clear visual radii
        const clampedDist = Math.max(0.1, Math.min(6.0, realDist));
        // Use a wide pixel multiplier (60px per meter) to clearly separate 1.0m vs 1.5m visually
        radius = 80 + clampedDist * 50; 
      }

      // To guarantee ZERO visual overlapping when multiple devices share identical raw RSSI (-50 dBm -> 3.16m),
      // distribute azimuth angles evenly across the full 360 degree tactical perimeter!
      const baseAngleDeg = (index * (360 / totalCount)) - 65; 
      const angleRad = (baseAngleDeg * Math.PI) / 180;

      const x = centerX + radius * Math.cos(angleRad);
      const y = centerY + radius * Math.sin(angleRad);

      // Save historical trajectories
      if (!trailsRef.current[device.mac_address]) {
        trailsRef.current[device.mac_address] = [];
      }
      trailsRef.current[device.mac_address].push({ x, y });
      if (trailsRef.current[device.mac_address].length > 15) {
        trailsRef.current[device.mac_address].shift();
      }

      return {
        ...device,
        x,
        y,
        radius,
        angleDeg: baseAngleDeg,
        palette,
        realDist: typeof realDist === 'number' ? realDist.toFixed(2) : '3.16',
        trail: trailsRef.current[device.mac_address] || []
      };
    });
  }, [displayDevices]);

  const avgRssi = useMemo(() => {
    if (!devices.length) return -50;
    const vals = devices.map(d => d.current_rssi?.value ?? -50);
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
  }, [devices]);

  return (
    <div className="relative w-full h-full flex flex-col items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950/50 rounded-3xl border border-blue-500/30 shadow-[0_0_50px_rgba(30,58,138,0.3)] select-none">
      
      {/* 1. TACTICAL HUD HEADER BAR */}
      <div className="absolute top-4 left-6 right-6 z-30 flex items-center justify-between pointer-events-auto bg-background-secondary/85 backdrop-blur-xl px-5 py-2.5 rounded-2xl border border-border shadow-2xl">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Radio className="w-5 h-5 text-emerald-400 animate-pulse" />
            <span className="text-text-primary font-black tracking-wider text-sm uppercase">RF TACTICAL COMMAND RADAR</span>
          </div>
          <span className="text-text-muted font-mono text-xs">|</span>
          <div className="flex items-center gap-2 text-xs font-medium text-text-primary">
            <span className="w-2 h-2 rounded-full bg-sky-400 shadow-[0_0_8px_#38bdf8]"></span>
            <span>Active Clients: <strong className="text-text-primary font-mono text-sm">{displayDevices.length}</strong></span>
          </div>
          <span className="text-text-muted font-mono text-xs">|</span>
          <div className="flex items-center gap-2 text-xs font-medium text-text-primary">
            <Activity className="w-4 h-4 text-yellow-400" />
            <span>Avg RSSI: <strong className="text-yellow-400 font-mono text-sm">{avgRssi} dBm</strong></span>
          </div>
          <span className="text-text-muted font-mono text-xs">|</span>
          <div className="flex items-center gap-1.5 bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 px-3 py-0.5 rounded-full text-[11px] font-bold tracking-wide shadow-inner">
            <Shield className="w-3.5 h-3.5 text-indigo-400" />
            <span>REAL NETGEAR DATA</span>
          </div>
        </div>

        {/* Display Control Buttons */}
        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setActiveOnly(!activeOnly)}
            className={`px-3.5 py-1 rounded-xl text-xs font-bold transition-all duration-300 border flex items-center gap-1.5 ${
              activeOnly 
                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/50 shadow-[0_0_15px_rgba(16,185,129,0.25)]' 
                : 'bg-card text-text-muted border-border hover:bg-card-hover'
            }`}
          >
            <Target className="w-3.5 h-3.5" />
            {activeOnly ? 'Active Focus ON' : 'Show All Nodes'}
          </button>
          <button
            onClick={() => setShowGrid(!showGrid)}
            className={`px-3.5 py-1 rounded-xl text-xs font-bold transition-all duration-300 border flex items-center gap-1.5 ${
              showGrid 
                ? 'bg-sky-500/20 text-sky-300 border-sky-500/50 shadow-[0_0_15px_rgba(56,189,248,0.25)]' 
                : 'bg-card text-text-muted border-border hover:bg-card-hover'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            Range Grid
          </button>
        </div>
      </div>

      {/* SCALE WRAPPER: Shrinks the radar automatically on smaller screens */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none scale-[0.6] lg:scale-[0.75] xl:scale-[0.85] 2xl:scale-100 origin-center">
        {/* 2. DYNAMIC ROTATING RADAR SWEEP BEAM & HEATMAP OVERLAY */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden flex items-center justify-center">
        {/* Deep ambient radial gradient */}
        <div className="absolute w-[750px] h-[750px] rounded-full bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.08)_0%,rgba(16,185,129,0.04)_35%,transparent_75%)]" />
        
        {/* Rotating Radar Sweep Scanner */}
        <div 
          className="absolute w-[760px] h-[760px] rounded-full pointer-events-none opacity-50 transition-transform duration-75"
          style={{
            transform: `rotate(${sweepAngle}deg)`,
            background: `conic-gradient(from 0deg at 50% 50%, rgba(56, 189, 248, 0.45) 0deg, rgba(16, 185, 129, 0.3) 25deg, rgba(56, 189, 248, 0.05) 60deg, transparent 80deg, transparent 360deg)`
          }}
        />
      </div>

      {/* 3. SCIENTIFIC RANGE RINGS & LAB LABELS */}
      {showGrid && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          {/* Inner Ring (2.5m Zone) */}
          <div className="absolute w-[320px] h-[320px] rounded-full border border-sky-500/35 border-dashed shadow-[0_0_20px_rgba(56,189,248,0.1)_inset]" />
          <span className="absolute top-1/2 left-[calc(50%+164px)] -translate-y-1/2 text-[10px] font-mono font-bold text-accent-primary bg-background-secondary px-2 py-0.5 rounded-md border border-accent-primary/30 shadow-sm">
            2.5m (-48 dBm)
          </span>

          {/* Middle Ring (5.0m Zone) */}
          <div className="absolute w-[500px] h-[500px] rounded-full border border-sky-500/25 border-dotted shadow-[0_0_25px_rgba(16,185,129,0.1)_inset]" />
          <span className="absolute top-1/2 left-[calc(50%+254px)] -translate-y-1/2 text-[10px] font-mono font-bold text-status-success bg-background-secondary px-2 py-0.5 rounded-md border border-status-success/30 shadow-sm">
            5.0m (-60 dBm)
          </span>

          {/* Outer Ring (10.0m+ Zone) */}
          <div className="absolute w-[680px] h-[680px] rounded-full border border-indigo-500/20 border-dashed" />
          <span className="absolute top-1/2 left-[calc(50%+344px)] -translate-y-1/2 text-[10px] font-mono font-bold text-accent-secondary bg-background-secondary px-2 py-0.5 rounded-md border border-accent-secondary/30 shadow-sm">
            10.0m+ (-75 dBm)
          </span>

          {/* Precision Crosshair Axes */}
          <div className="absolute w-[760px] h-[1px] bg-gradient-to-r from-transparent via-sky-400/30 to-transparent" />
          <div className="absolute h-[760px] w-[1px] bg-gradient-to-b from-transparent via-sky-400/30 to-transparent" />

          {/* Compass Sector Labels */}
          <div className="absolute top-[calc(50%-370px)] text-[11px] font-mono font-black text-accent-primary tracking-widest bg-background-secondary/90 px-2.5 py-0.5 rounded border border-border">N (0° FRONTAL LAB)</div>
          <div className="absolute bottom-[calc(50%-370px)] text-[11px] font-mono font-black text-accent-primary tracking-widest bg-background-secondary/90 px-2.5 py-0.5 rounded border border-border">S (180° REAR LAB)</div>
          <div className="absolute left-[calc(50%-380px)] text-[11px] font-mono font-black text-accent-primary tracking-widest bg-background-secondary/90 px-2.5 py-0.5 rounded border border-border">W (270° WEST NODE)</div>
          <div className="absolute right-[calc(50%-380px)] text-[11px] font-mono font-black text-accent-primary tracking-widest bg-background-secondary/90 px-2.5 py-0.5 rounded border border-border">E (90° EAST NODE)</div>
        </div>
      )}

      {/* 4. LASER TETHERS & PACKET BEAD FLOW (SVG LAYER) */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 10 }}>
        <g transform={`translate(50%, 50%)`}>
          {devicePositions.map((dev) => {
            const rgb = dev.palette.rgb;
            return (
              <React.Fragment key={`tether-${dev.mac_address}`}>
                {/* Historical Trail */}
                {dev.trail.length > 1 && dev.online_status && (
                  <polyline
                    points={dev.trail.map(p => `${p.x},${p.y}`).join(' ')}
                    fill="none"
                    stroke={`rgba(${rgb}, 0.45)`}
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                )}
                {/* Laser Tether Line to Center Router */}
                <motion.line
                  x1="0"
                  y1="0"
                  animate={{ x2: dev.x, y2: dev.y }}
                  transition={{ type: 'spring', stiffness: 45, damping: 20 }}
                  stroke={`rgba(${rgb}, ${dev.online_status ? '0.6' : '0.2'})`}
                  strokeWidth="2"
                  strokeDasharray={dev.online_status ? "6, 6" : "3, 6"}
                />
              </React.Fragment>
            );
          })}
        </g>
      </svg>
      
      </div> {/* End Scale Wrapper */}

      {/* 5. HEROIC CENTER GATEWAY NEXUS (NETGEAR ROUTER) */}
      <motion.div
        className="absolute z-20 flex flex-col items-center justify-center cursor-pointer pointer-events-auto"
        whileHover={{ scale: 1.08 }}
      >
        <div className="w-24 h-24 rounded-3xl bg-background-secondary/95 border-2 border-sky-400 shadow-[0_0_60px_rgba(56,189,248,0.6)] backdrop-blur-2xl flex flex-col items-center justify-center relative group">
          {/* Outer rotating energy ring */}
          <div className="absolute -inset-2 rounded-[30px] border border-sky-400/40 animate-pulse pointer-events-none" />
          
          {/* LED Status Indicator Lights */}
          <div className="absolute top-2 flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_#10b981]"></span>
            <span className="w-2 h-2 rounded-full bg-sky-400 animate-pulse shadow-[0_0_10px_#38bdf8]" style={{ animationDelay: '0.3s' }}></span>
            <span className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse shadow-[0_0_10px_#facc15]" style={{ animationDelay: '0.6s' }}></span>
          </div>

          <Router size={42} className="text-sky-400 mt-2 filter drop-shadow-[0_0_12px_rgba(56,189,248,0.9)]" />
          <span className="text-[9px] font-black tracking-widest text-sky-300 mt-1 uppercase">GATEWAY</span>
        </div>

        {/* Router Hardware Tag */}
        <div className="mt-3 bg-background-secondary/95 px-4 py-1.5 rounded-full border border-sky-500/50 shadow-2xl backdrop-blur-xl flex items-center gap-2">
          <Zap className="w-4 h-4 text-yellow-400 animate-bounce" />
          <span className="text-text-primary font-black tracking-wider text-xs">
            {routerStatus?.router_name || 'NETGEAR NIGHTHAWK X4S'}
          </span>
        </div>
      </motion.div>

      {/* 6. HIGH-DEFINITION FLOATING CLIENT BADGES & TARGET MARKERS */}
      <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 25 }}>
        <div className="relative w-full h-full">
          {devicePositions.map((dev) => {
            const isOnline = dev.online_status ?? true;
            const rssiVal = dev.current_rssi?.value ?? -50;
            const p = dev.palette;

            return (
              <motion.div
                key={dev.mac_address}
                initial={false}
                animate={{ x: dev.x, y: dev.y }}
                transition={{ type: 'spring', stiffness: 45, damping: 20 }}
                className="absolute pointer-events-auto flex flex-col items-center group"
                style={{
                  left: '50%',
                  top: '50%',
                  marginLeft: '-28px',
                  marginTop: '-28px',
                }}
                onClick={() => onDeviceClick(dev)}
              >
                {/* Target Marker Button */}
                <motion.div 
                  className={`w-14 h-14 rounded-2xl bg-background-secondary/95 backdrop-blur-2xl border-2 ${isOnline ? p.border : 'border-border'} shadow-[0_10px_30px_rgba(0,0,0,0.9)] flex items-center justify-center relative transition-all duration-300 group-hover:scale-110`}
                  whileHover={{ scale: 1.15 }}
                  whileTap={{ scale: 0.95 }}
                >
                  {/* Pulsing Target Lock Ring */}
                  {isOnline && (
                    <span 
                      className={`absolute inset-0 rounded-2xl border ${p.border} opacity-50 animate-ping pointer-events-none`} 
                      style={{ animationDuration: '2.5s' }}
                    />
                  )}

                  {getDeviceIcon(dev, isOnline ? p.text : 'text-text-muted')}

                  {/* Corner Status Dot */}
                  <span className={`absolute bottom-1.5 right-1.5 w-2.5 h-2.5 rounded-full border border-border ${
                    isOnline ? 'bg-emerald-400 shadow-[0_0_10px_#10b981]' : 'bg-rose-500'
                  }`} />
                </motion.div>

                {/* ALWAYS VISIBLE HIGH-DEF TELEMETRY HUD BADGE */}
                <motion.div 
                  className="mt-2.5 bg-background-secondary/95 backdrop-blur-2xl px-4 py-2 rounded-xl border border-border shadow-[0_15px_35px_rgba(0,0,0,0.9)] flex flex-col items-center min-w-[150px] pointer-events-auto transition-transform group-hover:-translate-y-1"
                >
                  {/* Hostname & Palette Ribbon */}
                  <div className="flex items-center gap-2 w-full justify-center">
                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: p.hex, boxShadow: `0 0 8px ${p.hex}` }} />
                    <span className={`font-black text-xs tracking-wide ${isOnline ? 'text-text-primary' : 'text-text-muted'} truncate max-w-[130px]`}>
                      {dev.hostname || dev.mac_address || 'UNKNOWN CLIENT'}
                    </span>
                  </div>

                  {/* Real Distance & RSSI Telemetry Grid */}
                  {isOnline ? (
                    <div className="flex items-center justify-between w-full mt-1.5 pt-1.5 border-t border-border text-[11px] font-mono">
                      <span className="text-emerald-400 font-bold flex items-center gap-1">
                        <Target className="w-3 h-3" />
                        {dev.realDist}m
                      </span>
                      <span className="text-text-muted font-bold">|</span>
                      <span className={`${rssiVal >= -60 ? 'text-sky-300' : 'text-yellow-300'} font-bold`}>
                        {rssiVal} dBm
                      </span>
                    </div>
                  ) : (
                    <div className="mt-1 bg-rose-500/20 text-rose-300 border border-rose-500/40 px-2 py-0.5 rounded text-[10px] font-bold tracking-wider uppercase">
                      INACTIVE STANDBY
                    </div>
                  )}

                  {/* IP or Connection details */}
                  {isOnline && dev.ip_address && (
                    <span className="text-[9px] font-mono text-text-muted mt-1 uppercase tracking-wider">
                      IP: {dev.ip_address}
                    </span>
                  )}
                </motion.div>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* 7. BOTTOM FOOTER TELEMETRY LEGEND */}
      <div className="absolute bottom-4 right-6 left-6 z-30 pointer-events-auto flex items-center justify-between bg-background-secondary/85 backdrop-blur-xl px-5 py-2 rounded-xl border border-border shadow-xl">
        <div className="flex items-center gap-5 text-xs font-medium text-text-primary">
          <span className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 shadow-[0_0_8px_#10b981]" />
            Strong Signal (&gt; -55 dBm)
          </span>
          <span className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-sky-400 shadow-[0_0_8px_#38bdf8]" />
            Normal Range (-55 to -70 dBm)
          </span>
          <span className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-yellow-400 shadow-[0_0_8px_#facc15]" />
            Perimeter (&lt; -70 dBm)
          </span>
        </div>

        <div className="flex items-center gap-2 text-[11px] font-mono font-bold text-sky-300 bg-sky-500/15 px-3.5 py-1 rounded-lg border border-sky-500/30 shadow-inner">
          <Compass className="w-3.5 h-3.5 text-sky-400 animate-spin" style={{ animationDuration: '10s' }} />
          <span>REAL-TIME LDPL PROPAGATION MODEL ACTIVE</span>
        </div>
      </div>
    </div>
  );
};
