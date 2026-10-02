import { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REST_URL = `${API_URL}/api/v1/operations`;

export function useOperations() {
  const [metrics, setMetrics] = useState<any>(null);
  const [services, setServices] = useState<any>(null);
  const [backups, setBackups] = useState<any[]>([]);
  const [diagnostics, setDiagnostics] = useState<any>(null);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [mRes, sRes, bRes, dRes] = await Promise.all([
        fetch(`${REST_URL}/metrics`),
        fetch(`${REST_URL}/services`),
        fetch(`${REST_URL}/backups`),
        fetch(`${REST_URL}/diagnostics`)
      ]);
      
      if (mRes.ok) setMetrics(await mRes.json());
      if (sRes.ok) setServices(await sRes.json());
      if (bRes.ok) setBackups(await bRes.json());
      if (dRes.ok) setDiagnostics(await dRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  const controlService = async (serviceName: string, action: string) => {
    try {
      await fetch(`${REST_URL}/services/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ service_name: serviceName, action })
      });
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const createBackup = async (type: string) => {
    try {
      await fetch(`${REST_URL}/backups/create`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type })
      });
      fetchData();
    } catch (e) {
      console.error(e);
    }
  };

  const restoreBackup = async (backupId: string) => {
    try {
      await fetch(`${REST_URL}/backups/restore/${backupId}`, { method: 'POST' });
    } catch (e) {
      console.error(e);
    }
  };

  const generateReport = async () => {
    try {
      const res = await fetch(`${REST_URL}/reports/generate`, { method: 'POST' });
      return res.json();
    } catch (e) {
      console.error(e);
    }
  };

  return {
    metrics,
    services,
    backups,
    diagnostics,
    controlService,
    createBackup,
    restoreBackup,
    generateReport,
    refreshData: fetchData
  };
}
