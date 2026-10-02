import React from 'react';
import { ConnectedDevice } from '../hooks/useNetworkData';
import { GroundTruth } from '../hooks/useDatasetCollection';

interface Props {
  devices: ConnectedDevice[];
  groundTruths: Record<string, GroundTruth>;
  onUpdate: (gt: GroundTruth) => void;
  disabled: boolean;
}

export const DeviceGroundTruth: React.FC<Props> = ({ devices, groundTruths, onUpdate, disabled }) => {
  return (
    <div className="flex-1 overflow-auto rounded-xl border border-border/50 custom-scrollbar relative">
      <table className="w-full text-left text-sm text-text-primary">
        <thead className="text-xs uppercase bg-card/80 text-text-muted sticky top-0 backdrop-blur-sm shadow-md z-10">
          <tr>
            <th className="px-2 py-3 text-center">Inc</th>
            <th className="px-2 py-3">Device</th>
            <th className="px-2 py-3 w-20">Dist(m)</th>
            <th className="px-2 py-3 w-20">Dir(°)</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {devices.map(device => {
            const gt = groundTruths[device.mac_address];
            if (!gt) return null;
            
            return (
              <tr key={device.mac_address} className={`transition-colors ${!gt.include_in_collection ? 'opacity-50' : 'hover:bg-card/30'}`}>
                <td className="px-2 py-2 text-center">
                  <input 
                    type="checkbox" 
                    checked={gt.include_in_collection}
                    disabled={disabled}
                    onChange={e => onUpdate({ ...gt, include_in_collection: e.target.checked })}
                    className="w-4 h-4 rounded border-border bg-card/50 text-blue-500 focus:ring-blue-500/50"
                  />
                </td>
                <td className="px-2 py-2 font-medium truncate max-w-[100px]" title={device.hostname || device.mac_address}>
                  {device.hostname || device.mac_address}
                </td>
                <td className="px-2 py-2">
                  <input 
                    type="number" step="0.1" min="0" 
                    value={gt.distance}
                    disabled={disabled || !gt.include_in_collection}
                    onChange={e => onUpdate({ ...gt, distance: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-card border border-border rounded p-1 text-xs text-text-primary focus:outline-none focus:border-blue-500"
                  />
                </td>
                <td className="px-2 py-2">
                  <input 
                    type="number" step="1" min="0" max="359"
                    value={gt.direction}
                    disabled={disabled || !gt.include_in_collection}
                    onChange={e => onUpdate({ ...gt, direction: parseFloat(e.target.value) || 0 })}
                    className="w-full bg-card border border-border rounded p-1 text-xs text-text-primary focus:outline-none focus:border-blue-500"
                  />
                </td>
              </tr>
            );
          })}
          {devices.length === 0 && (
            <tr><td colSpan={6} className="px-4 py-8 text-center text-text-muted italic">No devices detected.</td></tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
