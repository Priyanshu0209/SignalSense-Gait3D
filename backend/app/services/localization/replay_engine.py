import asyncio
import logging
import random
import os
import csv
from typing import Optional
from app.websockets.manager import websocket_manager
from app.services.ai.model_registry import get_model_registry

logger = logging.getLogger("signalsense.localization.replay")

class ReplayEngine:
    def __init__(self):
        self.is_playing = False
        self.dataset = None
        self.speed = 1.0
        self.current_index = 0
        self.total_samples = 0
        self.data_rows = []
        self.loop_task = None

    async def load_dataset(self, filename: str):
        datasets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "data", "datasets"))
        filepath = os.path.join(datasets_dir, filename)
        if not os.path.exists(filepath):
            raise FileNotFoundError("Dataset not found")
            
        self.data_rows = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.data_rows.append(row)
                
        self.total_samples = len(self.data_rows)
        self.current_index = 0
        self.dataset = filename
        
        await self._broadcast_state()

    async def play(self):
        if self.is_playing or not self.data_rows:
            return
        self.is_playing = True
        self.loop_task = asyncio.create_task(self._replay_loop())
        await self._broadcast_state()

    async def pause(self):
        if not self.is_playing:
            return
        self.is_playing = False
        if self.loop_task:
            self.loop_task.cancel()
            try:
                await self.loop_task
            except asyncio.CancelledError:
                pass
        await self._broadcast_state()

    async def seek(self, index: int):
        self.current_index = max(0, min(index, self.total_samples - 1))
        await self._broadcast_state()

    async def set_speed(self, speed: float):
        self.speed = speed
        await self._broadcast_state()

    async def _replay_loop(self):
        try:
            model_registry = get_model_registry()
            
            while self.is_playing and self.current_index < self.total_samples:
                row = self.data_rows[self.current_index]
                active_model = model_registry.get_active_model()
                
                # Extract GT
                mac = row.get("mac_address", "Unknown")
                gt_dist = float(row.get("distance", 0))
                gt_dir = float(row.get("direction", 0))
                rssi = float(row.get("rssi", -70))
                
                # Mock AI Prediction based on active model and RSSI
                if active_model:
                    base_dist = max(0.1, (rssi + 100) / 10.0)
                    # Use model accuracy to determine error magnitude (mock logic)
                    accuracy = active_model.accuracy / 100.0
                    error_factor = (1.0 - accuracy) * 5.0 # Max 5m error
                    est_dist = base_dist + random.uniform(-error_factor, error_factor)
                    est_dist = max(0.1, round(est_dist, 2))
                    confidence = random.randint(60, 99)
                else:
                    est_dist = gt_dist # fallback if no model
                    confidence = 0
                
                # Calculate Error
                abs_error = abs(est_dist - gt_dist)
                
                payload = {
                    "mac_address": mac,
                    "gt_distance": gt_dist,
                    "gt_direction": gt_dir,
                    "rssi": rssi,
                    "est_distance": est_dist,
                    "est_direction": gt_dir, # Simplify: assume model only predicts distance for now
                    "abs_error": round(abs_error, 2),
                    "confidence": confidence,
                    "index": self.current_index,
                    "total": self.total_samples,
                    "speed": self.speed,
                    "is_playing": self.is_playing
                }
                
                await websocket_manager.broadcast_event("localization_replay_frame", payload)
                
                self.current_index += 1
                
                # Sleep based on speed (assume original was 1 sample/sec for mock)
                await asyncio.sleep(1.0 / self.speed)
                
            if self.current_index >= self.total_samples:
                self.is_playing = False
                await self._broadcast_state()
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Replay loop error: {e}")
            self.is_playing = False

    async def _broadcast_state(self):
        state = {
            "dataset": self.dataset,
            "is_playing": self.is_playing,
            "speed": self.speed,
            "current_index": self.current_index,
            "total_samples": self.total_samples
        }
        await websocket_manager.broadcast_event("localization_replay_state", state)


replay_engine = ReplayEngine()

def get_replay_engine() -> ReplayEngine:
    return replay_engine
