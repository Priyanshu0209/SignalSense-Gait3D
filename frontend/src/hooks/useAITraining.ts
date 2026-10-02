import { useState, useEffect } from 'react';


const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REST_URL = `${API_URL}/api/v1/ai`;

export interface DatasetMeta {
  filename: string;
  name: string;
  size_mb: number;
  samples: number;
  devices: number;
  environment: string;
  duration: string;
  created_at: string;
  quality_score: number;
}

export interface ModelMeta {
  id: string;
  name: string;
  algorithm: string;
  training_date: string;
  dataset: string;
  accuracy: number;
  version: string;
  status: string;
}

export interface TrainingProgress {
  experiment_id: string;
  epoch: number;
  total_epochs: number;
  current_loss: number;
  val_score: number;
  elapsed_time: number;
  remaining_time: number;
  cpu_usage: number;
  memory_usage: number;
  log: string;
}

export interface LiveInference {
  mac_address: string;
  hostname: string;
  estimated_distance: number;
  confidence_pct: number;
  quality: 'Low' | 'Medium' | 'High';
  inference_time_ms: number;
}

export function useAITraining() {
  const [datasets, setDatasets] = useState<DatasetMeta[]>([]);
  const [models, setModels] = useState<ModelMeta[]>([]);
  const [experiments, setExperiments] = useState<any[]>([]);
  
  const [trainingProgress, setTrainingProgress] = useState<TrainingProgress | null>(null);
  const [liveInferences, setLiveInferences] = useState<Record<string, LiveInference>>({});

  useEffect(() => {
    fetchDatasets();
    fetchModels();
    fetchExperiments();

    let ws: WebSocket;
    let reconnectTimer: any;
    
    const connect = () => {
      const WS_URL_NATIVE = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
      ws = new WebSocket(WS_URL_NATIVE);
      
      ws.onmessage = (event) => {
        if (event.data === "pong") return;
        try {
          const payload = JSON.parse(event.data);
          if (payload.event === 'ai_training_progress') {
            setTrainingProgress(payload.data);
          } else if (payload.event === 'ai_training_completed') {
            setTrainingProgress(null);
            fetchModels();
            fetchExperiments();
          } else if (payload.event === 'ai_live_inference') {
            setLiveInferences(prev => {
              const updated = { ...prev };
              payload.data.forEach((inf: LiveInference) => updated[inf.mac_address] = inf);
              return updated;
            });
          }
        } catch (e) {
          console.error("WS Parse Error", e);
        }
      };

      ws.onclose = () => {
        reconnectTimer = setTimeout(connect, 3000);
      };
    };

    connect();

    return () => {
      if (reconnectTimer) clearTimeout(reconnectTimer);
      if (ws) ws.close();
    };
  }, []);

  const fetchDatasets = async () => {
    try {
      const res = await fetch(`${REST_URL}/datasets`);
      if (res.ok) setDatasets(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchModels = async () => {
    try {
      const res = await fetch(`${REST_URL}/models`);
      if (res.ok) setModels(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const fetchExperiments = async () => {
    try {
      const res = await fetch(`${REST_URL}/experiments`);
      if (res.ok) setExperiments(await res.json());
    } catch (e) {
      console.error(e);
    }
  };

  const deleteDataset = async (filename: string) => {
    try {
      await fetch(`${REST_URL}/datasets/${filename}`, { method: 'DELETE' });
      fetchDatasets();
    } catch (e) {
      console.error(e);
    }
  };

  const downloadDataset = (filename: string) => {
    window.open(`${REST_URL}/datasets/${filename}/download`, '_blank');
  };

  const startTraining = async (config: any) => {
    setTrainingProgress({
      experiment_id: 'pending',
      epoch: 0,
      total_epochs: config.epochs,
      current_loss: 0,
      val_score: 0,
      elapsed_time: 0,
      remaining_time: 0,
      cpu_usage: 0,
      memory_usage: 0,
      log: 'Initializing training...'
    });
    try {
      await fetch(`${REST_URL}/train/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
    } catch (e) {
      console.error(e);
    }
  };

  const stopTraining = async () => {
    try {
      await fetch(`${REST_URL}/train/stop`, { method: 'POST' });
      setTrainingProgress(null);
    } catch (e) {
      console.error(e);
    }
  };

  const activateModel = async (modelId: string) => {
    try {
      await fetch(`${REST_URL}/models/${modelId}/activate`, { method: 'POST' });
      fetchModels();
    } catch (e) {
      console.error(e);
    }
  };

  const deleteModel = async (modelId: string) => {
    try {
      await fetch(`${REST_URL}/models/${modelId}`, { method: 'DELETE' });
      fetchModels();
    } catch (e) {
      console.error(e);
    }
  };

  return {
    datasets,
    models,
    experiments,
    trainingProgress,
    liveInferences,
    startTraining,
    stopTraining,
    activateModel,
    deleteModel,
    deleteDataset,
    downloadDataset,
    refreshData: () => {
      fetchDatasets();
      fetchModels();
      fetchExperiments();
    }
  };
}
