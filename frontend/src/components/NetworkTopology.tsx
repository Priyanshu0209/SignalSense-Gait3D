import React from 'react';
import { ConnectedDevice, RouterStatus } from '../hooks/useNetworkData';
import { Router, Smartphone, Laptop, Tv, Cpu, Wifi } from 'lucide-react';

interface NetworkTopologyProps {
  devices: ConnectedDevice[];
  routerStatus: RouterStatus | null;
  onDeviceClick: (device: ConnectedDevice) => void;
}

const getDeviceIcon = (device: ConnectedDevice) => {
  const type = (device.device_type || '').toLowerCase();
  const name = (device.hostname || '').toLowerCase();
  
  if (type.includes('phone') || type.includes('mobile') || name.includes('moto') || name.includes('iphone') || name.includes('pixel') || name.includes('galaxy') || name.includes('samsung')) 
    return <Smartphone size={24} className="text-status-success" />;
    
  if (type.includes('laptop') || type.includes('pc') || type.includes('mac') || name.includes('laptop') || name.includes('macbook') || name.includes('desktop') || name.includes('pc')) 
    return <Laptop size={24} className="text-accent-secondary" />;
    
  if (type.includes('tv') || name.includes('tv')) 
    return <Tv size={24} className="text-status-warning" />;
    
  if (type.includes('iot')) 
    return <Cpu size={24} className="text-orange-500" />;
    
  return <Wifi size={24} className="text-accent-primary" />;
};

export const NetworkTopology: React.FC<NetworkTopologyProps> = ({ devices, routerStatus, onDeviceClick }) => {
  
  return (
    <div className="w-full h-full flex flex-col items-center overflow-auto bg-background-primary rounded-3xl border border-border shadow-sm p-8">
      
      {/* Header */}
      <div className="w-full flex items-center gap-3 mb-12">
        <div className="p-2 bg-accent-primary/10 rounded-xl border border-accent-primary/20">
          <Router size={24} className="text-accent-primary" />
        </div>
        <div>
          <h2 className="text-xl font-bold text-text-primary tracking-tight">Topology</h2>
          <p className="text-xs text-text-muted font-mono tracking-widest uppercase">Network Tree View</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col items-center pt-8 w-full min-w-max">
        
        {/* Router Node */}
        <div className="flex flex-col items-center">
          <div className="w-24 h-24 rounded-2xl bg-card border border-accent-primary flex flex-col items-center justify-center shadow-md relative z-10">
            <Router size={40} className="text-accent-primary mb-1" />
            <div className="absolute top-2 right-2 w-3 h-3 bg-status-success rounded-full border-2 border-card" />
          </div>
          <span className="mt-4 text-text-primary font-bold tracking-wide text-sm">
            {routerStatus?.router_name || 'CORE GATEWAY'}
          </span>
          <span className="mt-1 text-[10px] text-text-muted font-mono bg-card px-2 py-1 rounded border border-border">
            {routerStatus?.wan_ip || 'WAN ONLINE'}
          </span>
        </div>

        {devices.length > 0 && (
          <>
            {/* Trunk Line */}
            <div className="w-px h-12 bg-foreground/20"></div>

            {/* Horizontal Branching Line */}
            <div className="relative w-full flex justify-center h-px bg-foreground/20" style={{ width: `${(devices.length - 1) * 160}px`, maxWidth: '100%' }}></div>
            
            {/* Devices Row */}
            <div className="flex justify-center gap-4 mt-0">
              {devices.map((device) => (
                <div key={device.mac_address} className="flex flex-col items-center w-36">
                  {/* Stem */}
                  <div className="w-px h-8 bg-foreground/20"></div>
                  
                  {/* Device Card */}
                  <div 
                    onClick={() => onDeviceClick(device)}
                    className={`w-20 h-20 rounded-xl bg-card border ${device.online_status ? 'border-border cursor-pointer hover:border-accent-primary hover:-translate-y-1 transition-transform' : 'border-status-error/50 opacity-60'} flex items-center justify-center shadow-sm relative z-10 group`}
                  >
                    {getDeviceIcon(device)}
                    <div className={`absolute bottom-2 right-2 w-2 h-2 rounded-full border-2 border-card ${device.online_status ? 'bg-status-success' : 'bg-status-error'}`} />
                  </div>
                  
                  {/* Device Info */}
                  <span className="mt-3 text-text-primary font-bold text-xs truncate w-full text-center px-2">
                    {device.hostname || device.mac_address.substring(0, 8)}
                  </span>
                  <span className="text-[10px] font-mono text-text-muted mt-1 uppercase tracking-wider">
                    {device.ip_address}
                  </span>
                </div>
              ))}
            </div>
          </>
        )}
      </div>

    </div>
  );
};
