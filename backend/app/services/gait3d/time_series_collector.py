import asyncio
import logging
import time
import math
import random
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
from collections import deque

from app.services.device_state_manager import get_device_state_manager

logger = logging.getLogger("signalsense.gait3d.collector")

class GaitTimeSeriesCollector:

    def __init__(self, buffer_max_size: int = 400, sample_rate_hz: float = 20.0):
        self.buffer_max_size = buffer_max_size
        self.sample_rate_hz = sample_rate_hz
        self.sample_interval = 1.0 / sample_rate_hz
        
        # MAC Address -> deque of {"timestamp": float, "time_iso": str, "raw_rssi": float, "device_name": str}
        self.buffers: Dict[str, deque] = {}
        self.is_running = False
        # DISABLED by default: Real-world data-driven mode. Simulation can be toggled on from UI if needed.
        self.simulation_enabled = False 
        self.simulation_task: Optional[asyncio.Task] = None
        
        # Simulation parameter overrides (Only active if simulation is explicitly toggled ON by regression unit tests or diagnostics)
        self.sim_params: Dict[str, Dict[str, Any]] = {
            "00:1A:2B:3C:4D:5E": {
                "base_rssi": -52.0,
                "cadence_rpm": 112.0,
                "stride_depth_db": 5.4,
                "phase": 0.0,
                "activity": "Walking"
            },
            "AA:BB:CC:DD:EE:01": {
                "base_rssi": -64.0,
                "cadence_rpm": 0.0,
                "stride_depth_db": 0.8,
                "phase": 1.2,
                "activity": "Standing"
            },
            "A1:B2:C3:D4:E5:F6": {
                "base_rssi": -48.0,
                "cadence_rpm": 145.0,
                "stride_depth_db": 8.2,
                "phase": 2.5,
                "activity": "Running"
            }
        }

    async def start(self):
        if self.is_running:
            return
        self.is_running = True
        self.simulation_task = asyncio.create_task(self._collection_loop())
        logger.info(f"GaitTimeSeriesCollector started at {self.sample_rate_hz}Hz (Real Data Driven Mode).")

    async def stop(self):
        if not self.is_running:
            return
        self.is_running = False
        if self.simulation_task:
            self.simulation_task.cancel()
            try:
                await self.simulation_task
            except asyncio.CancelledError:
                pass
        logger.info("GaitTimeSeriesCollector stopped.")

    def set_simulation_state(self, enabled: bool, activity_override: Optional[str] = None):
        self.simulation_enabled = enabled
        if activity_override and activity_override in ["Still", "Standing", "Walking", "Running", "Sitting", "Falling"]:
            for mac in self.sim_params:
                self.sim_params[mac]["activity"] = activity_override
                if activity_override == "Walking":
                    self.sim_params[mac]["cadence_rpm"] = 110.0 + random.uniform(-6, 6)
                    self.sim_params[mac]["stride_depth_db"] = 5.0
                elif activity_override == "Running":
                    self.sim_params[mac]["cadence_rpm"] = 150.0 + random.uniform(-10, 10)
                    self.sim_params[mac]["stride_depth_db"] = 8.5
                elif activity_override == "Standing":
                    self.sim_params[mac]["cadence_rpm"] = 0.0
                    self.sim_params[mac]["stride_depth_db"] = 0.6
                elif activity_override == "Still":
                    self.sim_params[mac]["cadence_rpm"] = 0.0
                    self.sim_params[mac]["stride_depth_db"] = 0.1
                elif activity_override == "Sitting":
                    self.sim_params[mac]["cadence_rpm"] = 0.0
                    self.sim_params[mac]["stride_depth_db"] = 1.1
                elif activity_override == "Falling":
                    self.sim_params[mac]["cadence_rpm"] = 30.0
                    self.sim_params[mac]["stride_depth_db"] = 12.0
        logger.info(f"Simulation state updated: enabled={enabled}, override={activity_override}")

    def add_sample(self, mac_address: str, rssi: float, device_name: str = "Client Device"):
        if mac_address not in self.buffers:
            self.buffers[mac_address] = deque(maxlen=self.buffer_max_size)
        
        now = time.time()
        self.buffers[mac_address].append({
            "timestamp": now,
            "time_iso": datetime.now(timezone.utc).isoformat(),
            "raw_rssi": round(rssi, 3),
            "device_name": device_name
        })

    def get_device_history(self, mac_address: str) -> List[Dict[str, Any]]:
        if mac_address not in self.buffers:
            return []
        return list(self.buffers[mac_address])

    def get_all_macs(self) -> List[str]:
        return list(self.buffers.keys())

    def get_recent_window(self, mac_address: str, duration_sec: float = 5.0) -> List[Dict[str, Any]]:
        if mac_address not in self.buffers:
            return []
        now = time.time()
        cutoff = now - duration_sec
        return [s for s in self.buffers[mac_address] if s["timestamp"] >= cutoff]

    async def _collection_loop(self):
        try:
            device_mgr = get_device_state_manager()
            while self.is_running:
                start_time = time.time()
                
                # 1. REAL DATA INTEGRATION: Ingest discovered Wi-Fi devices from DeviceStateManager (Source of Truth)
                devices = device_mgr.get_all_devices()
                for dev in devices:
                    if dev.online_status and dev.current_rssi is not None:
                        val = dev.current_rssi.value if hasattr(dev.current_rssi, "value") else dev.current_rssi
                        if val is not None:
                            self.add_sample(dev.mac_address, float(val), dev.hostname or dev.mac_address)

                # 2. Synthetic signal generator ONLY runs if simulation is explicitly enabled by test automation
                if self.simulation_enabled:
                    t = time.time()
                    for mac, params in self.sim_params.items():
                        base = params["base_rssi"]
                        cadence = params["cadence_rpm"]
                        depth = params["stride_depth_db"]
                        phase = params["phase"]
                        activity = params["activity"]
                        
                        wobble = 0.6 * math.sin(2 * math.pi * 0.25 * t + phase)
                        step_osc = 0.0
                        if cadence > 0 and activity in ["Walking", "Running", "Falling"]:
                            freq_hz = cadence / 60.0
                            primary_wave = math.sin(2 * math.pi * freq_hz * t + phase)
                            harmonic_wave = 0.35 * math.sin(4 * math.pi * freq_hz * t + phase + 0.5)
                            step_osc = - (depth / 2.0) * (primary_wave + harmonic_wave)
                        elif activity == "Standing":
                            step_osc = 0.4 * math.sin(2 * math.pi * 0.8 * t)
                        elif activity == "Sitting":
                            step_osc = 0.3 * math.cos(2 * math.pi * 0.4 * t)
                            
                        noise = random.gauss(0.0, 0.35)
                        synth_rssi = base + wobble + step_osc + noise
                        self.add_sample(mac, synth_rssi, f"Sensor Node ({activity})")
                
                elapsed = time.time() - start_time
                sleep_time = max(0.005, self.sample_interval - elapsed)
                await asyncio.sleep(sleep_time)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in GaitTimeSeriesCollector loop: {e}", exc_info=True)

collector_singleton = GaitTimeSeriesCollector()

def get_gait_time_series_collector() -> GaitTimeSeriesCollector:
    return collector_singleton
