import { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REST_URL = `${API_URL}/api/v1/research`;

export function useResearch() {
  const [experiments, setExperiments] = useState<any[]>([]);
  const [provenance, setProvenance] = useState<any>({});
  const [validationWarnings, setValidationWarnings] = useState<any[]>([]);

  useEffect(() => {
    fetchExperiments();
    fetchProvenance();
    runValidation();
  }, []);

  const fetchExperiments = async () => {
    try {
      const res = await fetch(`${REST_URL}/experiments`);
      if (res.ok) setExperiments(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchProvenance = async () => {
    try {
      const res = await fetch(`${REST_URL}/provenance`);
      if (res.ok) setProvenance(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const runValidation = async () => {
    try {
      const res = await fetch(`${REST_URL}/validate`);
      if (res.ok) setValidationWarnings(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const getNotebook = async (expId: string) => {
    try {
      const res = await fetch(`${REST_URL}/notebook/${expId}`);
      if (res.ok) {
        const data = await res.json();
        return data.content;
      }
    } catch (e) {
      console.error(e);
    }
    return '';
  };

  const updateNotebook = async (expId: string, content: string) => {
    try {
      await fetch(`${REST_URL}/notebook/${expId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ content })
      });
    } catch (e) {
      console.error(e);
    }
  };

  const generatePublication = async (expId: string, title: string, abstract: string) => {
    try {
      const res = await fetch(`${REST_URL}/publication/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ exp_id: expId, title, abstract })
      });
      return res.json();
    } catch (e) {
      console.error(e);
    }
  };

  return {
    experiments,
    provenance,
    validationWarnings,
    getNotebook,
    updateNotebook,
    generatePublication,
    refreshData: () => {
      fetchExperiments();
      fetchProvenance();
      runValidation();
    }
  };
}
