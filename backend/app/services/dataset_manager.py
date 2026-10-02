import asyncio
import time
from datetime import datetime, timezone
import logging
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
from app.services.device_state_manager import get_device_state_manager
from app.services.dataset_writer import get_dataset_writer
from app.websockets.manager import websocket_manager

logger = logging.getLogger("signalsense.dataset_manager")

class GroundTruthConfig(BaseModel):
    mac_address: str
    distance: float = 0.0
    direction: float = 0.0
    orientation: str = "Front"
    los: str = "Yes"
    environment: str = "Indoor"
    include_in_collection: bool = True
    rssi_0: float = -45.0
    n_value: float = 2.5

class DatasetCollectionConfig(BaseModel):
    session_name: str = "Default_Session"
    environment: str = "Indoor - Office"
    collector_device: str = "Default Collector"
    samples_per_device: int = 100
    sampling_interval: float = 1.0
    stabilization_time: float = 3.0
    readings_per_sample: int = 1

class DatasetManager:
    def __init__(self):
        self.device_state_manager = get_device_state_manager()
        self.dataset_writer = get_dataset_writer()
        
        self.config = DatasetCollectionConfig()
        self.ground_truth_map: Dict[str, GroundTruthConfig] = {}
        
        self.is_running = False
        self.is_paused = False
        self.collection_task = None
        
        self.start_time = None
        self.end_time = None
        self.total_samples_collected = 0
        self.samples_per_mac: Dict[str, int] = {}
        
        self.coverage_matrix = {} # {(distance, direction): count}
        self.quality_stats = {
            "rssi_sum": 0,
            "rssi_count": 0,
            "missing_samples": 0
        }

    def set_config(self, config: DatasetCollectionConfig):
        if self.is_running:
            raise ValueError("Cannot change config while session is running.")
        self.config = config

    def set_ground_truth(self, mac: str, gt: GroundTruthConfig):
        self.ground_truth_map[mac] = gt
        asyncio.create_task(websocket_manager.broadcast_event("dataset_gt_updated", {"mac": mac, "gt": gt.model_dump()}))

    def get_ground_truth(self) -> List[GroundTruthConfig]:
        return list(self.ground_truth_map.values())

    async def start_collection(self):
        if self.is_running:
            return
            
        logger.info("Starting Dataset Collection Session...")
        await self.dataset_writer.start_session(
            session_name=self.config.session_name,
            environment=self.config.environment,
            collector_device=self.config.collector_device
        )
        
        self.is_running = True
        self.is_paused = False
        self.start_time = time.time()
        self.total_samples_collected = 0
        self.samples_per_mac = {mac: 0 for mac, gt in self.ground_truth_map.items() if gt.include_in_collection}
        
        self.coverage_matrix = {}
        self.quality_stats = {"rssi_sum": 0, "rssi_count": 0, "missing_samples": 0}
        
        # Emit state update
        await self._broadcast_state()
        
        # Allow stabilization
        if self.config.stabilization_time > 0:
            await asyncio.sleep(self.config.stabilization_time)
            
        self.collection_task = asyncio.create_task(self._collection_loop())

    async def pause_collection(self):
        if self.is_running and not self.is_paused:
            self.is_paused = True
            await self._broadcast_state()

    async def resume_collection(self):
        if self.is_running and self.is_paused:
            self.is_paused = False
            await self._broadcast_state()

    async def stop_collection(self):
        if not self.is_running:
            return
            
        self.is_running = False
        self.is_paused = False
        self.end_time = time.time()
        
        if self.collection_task:
            self.collection_task.cancel()
            try:
                await self.collection_task
            except asyncio.CancelledError:
                pass
                
        # Generate Metadata
        metadata = self._generate_metadata()
        await self.dataset_writer.stop_session(metadata)
        
        await self._broadcast_state()

    def _generate_metadata(self):
        devices = [mac for mac, gt in self.ground_truth_map.items() if gt.include_in_collection]
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        return {
            "Session Name": self.config.session_name,
            "Start Time": datetime.fromtimestamp(self.start_time, tz=timezone.utc).isoformat() if self.start_time else None,
            "End Time": datetime.fromtimestamp(self.end_time, tz=timezone.utc).isoformat() if self.end_time else None,
            "Total Duration": f"{total_duration:.2f} seconds",
            "Number of Devices": len(devices),
            "Number of Samples": self.total_samples_collected,
            "Environment": self.config.environment,
            "Collector": self.config.collector_device,
            "Router": "Default Router"
        }

    async def _collection_loop(self):
        try:
            while self.is_running:
                if self.is_paused:
                    await asyncio.sleep(0.5)
                    continue
                    
                try:
                    start_loop_time = time.time()

                    # Check if we reached target samples for all active devices
                    active_macs = [mac for mac, gt in self.ground_truth_map.items() if gt.include_in_collection]
                    if not active_macs:
                        logger.warning("No devices selected for dataset collection. Stopping.")
                        await self.stop_collection()
                        break
                        
                    all_done = all(self.samples_per_mac.get(mac, 0) >= self.config.samples_per_device for mac in active_macs)
                    if all_done:
                        logger.info("Target samples reached for all devices. Stopping collection.")
                        await self.stop_collection()
                        break
                        
                    # Collect a sample for each included device
                    devices = self.device_state_manager.get_all_devices()
                    device_dict = {d.mac_address: d for d in devices}
                    
                    samples_emitted = []
                    
                    for mac in active_macs:
                        if self.samples_per_mac.get(mac, 0) >= self.config.samples_per_device:
                            continue
                            
                        gt = self.ground_truth_map[mac]
                        device = device_dict.get(mac)
                        
                        if not device:
                            self.quality_stats["missing_samples"] += 1
                            continue # Device not currently detected
                            
                        # Build sample row
                        timestamp = datetime.now(timezone.utc).isoformat()
                        rssi_val = device.current_rssi.value if hasattr(device.current_rssi, 'value') else device.current_rssi
                        rssi_val = rssi_val if rssi_val is not None else -100
                        
                        sample = {
                            "Timestamp": timestamp,
                            "Session ID": self.dataset_writer.session_id,
                            "Device Name": device.hostname or "Unknown",
                            "MAC Address": device.mac_address,
                            "Ground Truth Distance": gt.distance,
                            "Ground Truth Direction": gt.direction,
                            "Orientation": gt.orientation,
                            "LOS": gt.los,
                            "Environment": gt.environment,
                            "RSSI": rssi_val,
                            "Signal Quality": getattr(device, 'signal_quality', 0)
                        }
                        
                        await self.dataset_writer.enqueue_sample(sample)
                        
                        # Update stats
                        self.samples_per_mac[mac] += 1
                        self.total_samples_collected += 1
                        if rssi_val != -100:
                            self.quality_stats["rssi_sum"] += rssi_val
                            self.quality_stats["rssi_count"] += 1
                            
                        # Update coverage matrix
                        matrix_key = (gt.distance, gt.direction)
                        self.coverage_matrix[matrix_key] = self.coverage_matrix.get(matrix_key, 0) + 1
                        
                        samples_emitted.append(sample)
                        
                    if samples_emitted:
                        # Broadcast live samples for UI
                        await websocket_manager.broadcast_event("dataset_live_samples", samples_emitted)
                        await self._broadcast_state()
                        
                    # Sleep until next interval
                    elapsed = time.time() - start_loop_time
                    sleep_time = max(0.1, self.config.sampling_interval - elapsed)
                    await asyncio.sleep(sleep_time)
                except Exception as inner_e:
                    logger.error(f"INNER LOOP EXCEPTION: {inner_e}")
                    import traceback
                    logger.error(traceback.format_exc())
                    await asyncio.sleep(1.0)
                
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Error in dataset collection loop: {e}")
            await self.stop_collection()

    def get_state(self):
        duration = 0
        if self.is_running and self.start_time:
            duration = time.time() - self.start_time
        elif self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            
        avg_rssi = (self.quality_stats["rssi_sum"] / self.quality_stats["rssi_count"]) if self.quality_stats["rssi_count"] > 0 else 0
        
        # Calculate dataset completeness
        active_macs = [mac for mac, gt in self.ground_truth_map.items() if gt.include_in_collection]
        target_total = len(active_macs) * self.config.samples_per_device if active_macs else 1
        completeness = min(100.0, (self.total_samples_collected / target_total) * 100.0) if target_total > 0 else 0
        
        # Convert coverage matrix keys to strings for JSON serialization
        json_coverage = {f"{dist}_{dir}": count for (dist, dir), count in self.coverage_matrix.items()}
        
        return {
            "status": "Running" if self.is_running and not self.is_paused else ("Paused" if self.is_paused else "Stopped"),
            "session_id": self.dataset_writer.session_id,
            "total_samples": self.total_samples_collected,
            "duration": duration,
            "samples_per_mac": self.samples_per_mac,
            "quality": {
                "avg_rssi": round(avg_rssi, 2),
                "missing_samples": self.quality_stats["missing_samples"],
                "completeness": round(completeness, 2),
                "quality_score": round(max(0, completeness - (self.quality_stats["missing_samples"] * 0.1)), 2) # Arbitrary simple metric
            },
            "coverage_matrix": json_coverage
        }
        
    async def _broadcast_state(self):
        state = self.get_state()
        await websocket_manager.broadcast_event("dataset_state_updated", state)

dataset_manager = DatasetManager()

def get_dataset_manager() -> DatasetManager:
    return dataset_manager
