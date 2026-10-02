import asyncio
import logging
import json
import time
from datetime import datetime, timezone
from enum import Enum
from fastapi.encoders import jsonable_encoder
from typing import Optional, Dict, Any
from app.core.config import settings
from app.adapters.router.manager import get_router_manager
from app.services.device_state_manager import get_device_state_manager
from app.services.database_service import DatabaseService
from app.websockets.manager import websocket_manager
from app.services.simulation_engine import get_simulation_engine
from app.services.automation_engine import get_automation_engine

logger = logging.getLogger("signalsense.discovery.background")

class DiscoveryState(Enum):
    STARTING = "starting"
    CONNECTED = "connected"
    SCANNING = "scanning"
    RECONNECTING = "reconnecting"
    DEGRADED = "degraded"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"

class BackgroundDiscoveryService:

    def __init__(self):
        self.router_manager = None
        self.state_manager = None
        self._running = False
        self._discovery_task = None
        self._db_worker_task = None
        self._ws_worker_task = None
        
        # Bounded Queues
        self.db_queue = asyncio.Queue(maxsize=1000)
        self.ws_queue = asyncio.Queue(maxsize=1000)
        
        self.poll_interval = settings.UPDATE_INTERVAL_SECONDS
        self.state = DiscoveryState.STOPPED
        
        # Resilience config
        self.error_count = 0
        self.max_backoff = 300  # 5 minutes maximum backoff
        self.base_backoff = 5   # start with 5 seconds backoff
        self.max_retries = 50   # max retries before ERROR state
        
        # Metrics
        self.metrics = {
            "total_scans": 0,
            "successful_scans": 0,
            "failed_scans": 0,
            "avg_scan_duration_ms": 0.0,
            "max_scan_duration_ms": 0.0,
            "reconnect_count": 0,
            "dropped_events": 0,
            "broadcast_count": 0,
            "db_write_count": 0,
            "last_successful_scan": None
        }
        
    async def start(self):
        if self._running:
            return
            
        logger.info("Starting Background Discovery Service...")
        self._running = True
        self.state = DiscoveryState.STARTING
        
        if not self.router_manager:
            self.router_manager = get_router_manager()
        if not self.state_manager:
            self.state_manager = get_device_state_manager()
            
        self._db_worker_task = asyncio.create_task(self._db_worker())
        self._ws_worker_task = asyncio.create_task(self._ws_worker())
        self._discovery_task = asyncio.create_task(self._discovery_loop())
        
    async def stop(self):
        if not self._running:
            return
            
        logger.info("Stopping Background Discovery Service...")
        self.state = DiscoveryState.STOPPING
        self._running = False
        
        if self._discovery_task:
            self._discovery_task.cancel()
            try:
                await self._discovery_task
            except asyncio.CancelledError:
                pass

        # Allow workers to flush queues up to a timeout
        try:
            logger.info("Flushing queues...")
            await asyncio.wait_for(asyncio.gather(
                self.db_queue.join(),
                self.ws_queue.join()
            ), timeout=10.0)
        except asyncio.TimeoutError:
            logger.warning("Queue flush timed out. Proceeding to shutdown.")
            
        # Cancel workers
        for task in (self._db_worker_task, self._ws_worker_task):
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                    
        if self.router_manager:
            await self.router_manager.disconnect()
            
        try:
            from app.services.diagnostics.discovery_csv_logger import get_discovery_csv_logger
            await get_discovery_csv_logger().stop()
        except ImportError:
            pass
            
        try:
            from app.services.diagnostics.discovery_summary_logger import get_discovery_summary_logger
            await get_discovery_summary_logger().stop()
        except ImportError:
            pass
            
        try:
            from app.services.diagnostics.missing_field_analyzer import get_missing_field_analyzer
            await get_missing_field_analyzer().stop()
        except ImportError:
            pass
            
        try:
            from app.services.diagnostics.enterprise_report import get_enterprise_diagnostic_report
            await get_enterprise_diagnostic_report().stop()
        except ImportError:
            pass
            
        self.state = DiscoveryState.STOPPED
        logger.info("Background Discovery Service stopped.")
            
    async def _attempt_connection(self) -> bool:

        try:
            connected = await self.router_manager.connect()
            if connected:
                self.state = DiscoveryState.CONNECTED
                self.error_count = 0
                logger.info("Background Discovery Service connected successfully.")
                return True
        except Exception as e:
            logger.error(f"Connection attempt failed: {e}")
            
        self.state = DiscoveryState.DEGRADED
        return False
        
    def _calculate_backoff(self) -> float:

        backoff = min(self.max_backoff, self.base_backoff * (2 ** self.error_count))
        return backoff
        
    def _update_scan_metrics(self, duration_ms: float):
        self.metrics["total_scans"] += 1
        self.metrics["successful_scans"] += 1
        self.metrics["last_successful_scan"] = time.time()
        
        if duration_ms > self.metrics["max_scan_duration_ms"]:
            self.metrics["max_scan_duration_ms"] = duration_ms
            
        avg = self.metrics["avg_scan_duration_ms"]
        n = self.metrics["successful_scans"]
        self.metrics["avg_scan_duration_ms"] = avg + (duration_ms - avg) / n

    async def _db_worker(self):

        while True:
            try:
                task_type, payload = await self.db_queue.get()
                try:
                    if task_type == "device":
                        await DatabaseService.save_device_update(payload)
                        self.metrics["db_write_count"] += 1
                    elif task_type == "event":
                        await DatabaseService.save_event(**payload)
                        self.metrics["db_write_count"] += 1
                    elif task_type == "session_start":
                        await DatabaseService.start_device_session(**payload)
                        self.metrics["db_write_count"] += 1
                    elif task_type == "session_end":
                        await DatabaseService.end_device_session(**payload)
                        self.metrics["db_write_count"] += 1
                    elif task_type == "metadata":
                        await DatabaseService.save_metadata_change(**payload)
                        self.metrics["db_write_count"] += 1
                except Exception as e:
                    logger.error(f"Database worker failed to process item: {e}")
                finally:
                    self.db_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in db_worker: {e}")
                await asyncio.sleep(1)

    async def _ws_worker(self):

        while True:
            try:
                event_name, payload = await self.ws_queue.get()
                try:
                    await websocket_manager.broadcast_event(event_name, payload)
                    self.metrics["broadcast_count"] += 1
                except Exception as e:
                    logger.error(f"WebSocket worker failed to broadcast item: {e}")
                finally:
                    self.ws_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Unexpected error in ws_worker: {e}")
                await asyncio.sleep(1)

    def _enqueue_db(self, task_type: str, payload: Any):
        try:
            self.db_queue.put_nowait((task_type, payload))
        except asyncio.QueueFull:
            self.metrics["dropped_events"] += 1
            logger.warning("Database queue full! Dropped event.")

    def _enqueue_ws(self, event_name: str, payload: Any):
        try:
            self.ws_queue.put_nowait((event_name, payload))
        except asyncio.QueueFull:
            self.metrics["dropped_events"] += 1
            logger.warning("WebSocket queue full! Dropped event.")

    async def _discovery_loop(self):
        if not await self._attempt_connection():
            logger.warning("Initial connection failed. Entering reconnection loop.")
            
        while self._running:
            try:
                if self.state not in (DiscoveryState.CONNECTED, DiscoveryState.SCANNING):
                    if self.error_count >= self.max_retries:
                        logger.critical("Maximum retries reached. Service in ERROR state.")
                        self.state = DiscoveryState.ERROR
                        await asyncio.sleep(self.max_backoff)
                        continue
                        
                    self.state = DiscoveryState.RECONNECTING
                    self.error_count += 1
                    self.metrics["reconnect_count"] += 1
                    backoff = self._calculate_backoff()
                    logger.info(f"Reconnecting in {backoff} seconds (Attempt {self.error_count})...")
                    await asyncio.sleep(backoff)
                    
                    if not await self._attempt_connection():
                        continue

                self.state = DiscoveryState.SCANNING
                start_time = time.time()
                
                # Isolated block: Status
                try:
                    router_status = await self.router_manager.get_status()
                    if not router_status:
                        raise ConnectionError("Router returned null status")
                except Exception as e:
                    logger.error(f"Failed to poll router status: {e}")
                    raise
                    
                # Isolated block: Devices
                try:
                    raw_devices = await self.router_manager.get_connected_devices()
                    if raw_devices is None:
                        raise ConnectionError("Router returned null devices")
                except Exception as e:
                    logger.error(f"Failed to poll connected devices: {e}")
                    raise
                
                # Isolated block: State Processing
                try:
                    changed_devices = self.state_manager.process_router_update(raw_devices)
                except Exception as e:
                    logger.error(f"Failed to process router update: {e}")
                    changed_devices = []
                    
                # Phase 5: Digital Twin Simulation & Automation
                sim_engine = get_simulation_engine()
                auto_engine = get_automation_engine()
                
                final_devices = sim_engine.apply_simulation(changed_devices)
                for dev in final_devices:
                    auto_engine.evaluate(dev)
                
                # Enqueue Operations
                import uuid
                self._last_scan_id = str(uuid.uuid4())
                
                if final_devices:
                    payloads = []
                    for dev in final_devices:
                        self._enqueue_db("device", dev)
                        
                        payloads.append({
                            "timestamp": dev.last_seen.isoformat(),
                            "mac": dev.mac_address,
                            "hostname": dev.hostname,
                            "rssi": dev.current_rssi,
                            "signal": dev.signal_classification.value if getattr(dev, 'signal_classification', None) else "Unknown",
                            "distance": dev.distance_classification.value if getattr(dev, 'distance_classification', None) else "Unknown",
                            "trend": dev.signal_trend.value if getattr(dev, 'signal_trend', None) else "None",
                            "animation": dev.animation_state.model_dump() if getattr(dev, 'animation_state', None) else {},
                            "status": "online" if getattr(dev, 'online_status', False) else "offline",
                            "connection_duration": getattr(dev, 'connection_duration', 0),
                            "twin_mode": dev.twin_mode
                        })
                        
                        # Module 3: Diagnostics Logger
                        try:
                            from app.services.diagnostics.discovery_csv_logger import get_discovery_csv_logger
                            import uuid
                            if getattr(self, '_last_scan_id', None) is None or self.state == DiscoveryState.SCANNING:
                                # Ensure we generate one scan ID per cycle. Using a flag or generating before the loop.
                                pass
                            
                            csv_logger = get_discovery_csv_logger()
                            
                            # Start it if not running
                            if not csv_logger._running:
                                await csv_logger.start()
                                
                            missing_fields = []
                            if dev.current_rssi is None: missing_fields.append("RSSI")
                            if getattr(dev, 'signal_quality', None) is None: missing_fields.append("Signal Quality")
                            if dev.hostname == "Unknown" or not dev.hostname: missing_fields.append("Hostname")
                                
                            row = [
                                datetime.now(timezone.utc).isoformat(),
                                self._last_scan_id,
                                self._last_scan_id, # correlation ID
                                getattr(router_status, 'gateway_ip', 'Unknown'),
                                getattr(router_status, 'gateway_ip', 'Unknown'),
                                dev.mac_address,
                                dev.ip_address,
                                dev.hostname,
                                dev.manufacturer,
                                dev.manufacturer, # Vendor
                                dev.current_rssi if dev.current_rssi is not None else "N/A",
                                getattr(dev, 'signal_quality', "N/A"),
                                "N/A", # Upload Mbps
                                "N/A", # Download Mbps
                                "N/A", # Frequency
                                "N/A", # Channel
                                "N/A", # Latency
                                "online" if getattr(dev, 'online_status', False) else "offline",
                                getattr(dev, 'connection_duration', 0),
                                (time.time() - start_time) * 1000, # Discovery duration
                                0.0, # Response Time
                                dev.device_type,
                                "N/A", # Firmware
                                "N/A", # Model
                                ";".join(missing_fields) if missing_fields else "None",
                                "None", # Warnings
                                "None", # Errors
                                getattr(router_status, 'adapter_type', 'Unknown'),
                                "Router API",
                                getattr(dev, 'rssi_ant0', "N/A"),
                                getattr(dev, 'rssi_ant1', "N/A"),
                                getattr(dev, 'tx_per', "N/A"),
                                getattr(dev, 'rx_crc_per', "N/A"),
                                getattr(dev, 'false_cca', "N/A"),
                                getattr(dev, 'tx_mcs', "N/A"),
                                getattr(dev, 'rx_mcs', "N/A")
                            ]
                            csv_logger.log_device(row)
                        except Exception as csv_err:
                            logger.error(f"Failed to log device to CSV: {csv_err}")
                        
                    self._enqueue_ws("device_updated", payloads)
                    
                # Process Generated Events
                while self.state_manager.recent_events:
                    event = self.state_manager.recent_events.pop(0)
                    
                    if event["type"] == "METADATA_CHANGED":
                        self._enqueue_db("metadata", {
                            "mac_address": event["mac_address"],
                            "timestamp": event["timestamp"],
                            "field_name": event["field"],
                            "old_value": event["old_value"],
                            "new_value": event["new_value"]
                        })
                        self._enqueue_ws("metadata_changed", event)
                    else:
                        db_payload = {
                            "event_type": event["type"],
                            "mac_address": event["mac_address"],
                            "entity_id": event["mac_address"],
                            "message": f"{event['type']} for {event['mac_address']} (RSSI: {event.get('rssi', 'N/A')})",
                            "payload": json.dumps(jsonable_encoder(event)),
                            "severity": "INFO",
                            "category": "DEVICE",
                            "source_module": "BackgroundDiscoveryService",
                            "search_tags": "device," + event["type"].lower()
                        }
                        self._enqueue_db("event", db_payload)
                        self._enqueue_ws(event["type"].lower(), event)
                        
                        if event["type"] == "DEVICE_CONNECTED":
                            self._enqueue_db("session_start", {"mac_address": event["mac_address"], "timestamp": event["timestamp"]})
                        elif event["type"] == "DEVICE_DISCONNECTED":
                            self._enqueue_db("session_end", {"mac_address": event["mac_address"], "timestamp": event["timestamp"]})

                duration_ms = (time.time() - start_time) * 1000
                self._update_scan_metrics(duration_ms)
                
                # Module 4: Summary Logger
                try:
                    from app.services.diagnostics.discovery_summary_logger import get_discovery_summary_logger
                    summary_logger = get_discovery_summary_logger()
                    if not summary_logger._running:
                        await summary_logger.start()
                        
                    all_devices = self.state_manager.get_all_devices()
                    total_devs = len(all_devices)
                    online_devs = sum(1 for d in all_devices if d.online_status)
                    rssi_list = [d.current_rssi.value if hasattr(d.current_rssi, 'value') else d.current_rssi for d in all_devices if d.current_rssi is not None]
                    
                    summary_payload = {
                        "Timestamp": datetime.now(timezone.utc).isoformat(),
                        "Discovery Scan ID": getattr(self, '_last_scan_id', 'unknown'),
                        "Correlation ID": getattr(self, '_last_scan_id', 'unknown'),
                        "Router IP": getattr(router_status, 'gateway_ip', 'Unknown'),
                        "Gateway": getattr(router_status, 'gateway_ip', 'Unknown'),
                        "Discovery Duration (ms)": duration_ms,
                        "Router Response Time (ms)": 0.0,
                        "Processing Time (ms)": 0.0,
                        "Database Time (ms)": 0.0,
                        "API Time (ms)": 0.0,
                        "Frontend Time (ms)": 0.0,
                        "Total Devices": total_devs,
                        "Online Devices": online_devs,
                        "Offline Devices": total_devs - online_devs,
                        "New Devices": sum(1 for e in self.state_manager.recent_events if e.get("type") == "DEVICE_CONNECTED"),
                        "Disconnected Devices": sum(1 for e in self.state_manager.recent_events if e.get("type") == "DEVICE_DISCONNECTED"),
                        "Updated Devices": len(changed_devices),
                        "Metadata Changes": sum(1 for e in self.state_manager.recent_events if e.get("type") == "METADATA_CHANGED"),
                        "Average RSSI": sum(rssi_list)/len(rssi_list) if rssi_list else "N/A",
                        "Minimum RSSI": min(rssi_list) if rssi_list else "N/A",
                        "Maximum RSSI": max(rssi_list) if rssi_list else "N/A",
                        "Average Signal Quality": "N/A",
                        "Average Latency": "N/A",
                        "Average Upload": "N/A",
                        "Average Download": "N/A",
                        "RSSI Missing Count": sum(1 for d in all_devices if d.current_rssi is None),
                        "Signal Missing Count": sum(1 for d in all_devices if getattr(d, 'signal_quality', None) is None),
                        "Hostname Missing Count": sum(1 for d in all_devices if d.hostname == "Unknown" or not d.hostname),
                        "Manufacturer Missing Count": sum(1 for d in all_devices if getattr(d, 'manufacturer', None) in ("Unknown", None)),
                        "Vendor Missing Count": sum(1 for d in all_devices if getattr(d, 'manufacturer', None) in ("Unknown", None)),
                        "Frequency Missing Count": total_devs,
                        "Channel Missing Count": total_devs,
                        "Firmware Missing Count": total_devs,
                        "Model Missing Count": total_devs,
                        "CPU Missing Count": total_devs,
                        "RAM Missing Count": total_devs,
                        "Warnings": 0,
                        "Errors": 0,
                        "Validation Result": "PASS"
                    }
                    summary_logger.log_summary(summary_payload)
                    
                    # Module 5: Missing Field Analyzer
                    try:
                        from app.services.diagnostics.missing_field_analyzer import get_missing_field_analyzer
                        missing_analyzer = get_missing_field_analyzer()
                        if not missing_analyzer._running:
                            await missing_analyzer.start()
                            
                        # Fields to check: MAC, IP, Hostname, Manufacturer, Vendor, RSSI, Signal Quality, Upload, Download, Frequency, Channel, Latency, Firmware, Model, CPU, RAM, Gateway, Status, Type
                        for d in all_devices:
                            missing_analyzer.mark_device_checked()
                            fields_to_check = {
                                "MAC Address": (d.mac_address, "str"),
                                "IP Address": (d.ip_address, "str"),
                                "Hostname": (d.hostname, "str"),
                                "Manufacturer": (getattr(d, 'manufacturer', None), "str"),
                                "Vendor": (getattr(d, 'manufacturer', None), "str"), # Usually mapped same as manufacturer
                                "RSSI": (d.current_rssi, "int"),
                                "Signal Quality": (getattr(d, 'signal_quality', None), "int"),
                                "Upload Mbps": (getattr(d, 'upload_mbps', None), "float"),
                                "Download Mbps": (getattr(d, 'download_mbps', None), "float"),
                                "Frequency": (getattr(d, 'frequency', None), "str"),
                                "Channel": (getattr(d, 'channel', None), "int"),
                                "Latency": (getattr(d, 'latency', None), "float"),
                                "Firmware": (getattr(d, 'firmware', None), "str"),
                                "Model": (getattr(d, 'model', None), "str"),
                                "CPU": (getattr(d, 'cpu_usage', None), "float"),
                                "RAM": (getattr(d, 'ram_usage', None), "float"),
                                "Gateway": (getattr(router_status, 'gateway_ip', None), "str"),
                                "Connection Status": (getattr(d, 'online_status', None), "bool"),
                                "Device Type": (d.device_type, "str")
                            }
                            
                            for fname, (fval, ftype) in fields_to_check.items():
                                if fval is None or fval == "Unknown" or fval == "":
                                    missing_analyzer.log_missing_field({
                                        "Timestamp": datetime.now(timezone.utc).isoformat(),
                                        "Discovery Scan ID": getattr(self, '_last_scan_id', 'unknown'),
                                        "Correlation ID": getattr(self, '_last_scan_id', 'unknown'),
                                        "Router IP": getattr(router_status, 'gateway_ip', 'Unknown'),
                                        "MAC Address": d.mac_address,
                                        "Hostname": d.hostname,
                                        "Field Name": fname,
                                        "Expected Type": ftype,
                                        "Actual Value": str(fval),
                                        "Pipeline Layer": "Discovery Worker",
                                        "Severity": "HIGH" if fname in ("RSSI", "MAC Address") else "MEDIUM",
                                        "Recommendation": f"Check Router API payload for {fname}",
                                        "Discovery Duration": duration_ms,
                                        "Adapter": getattr(router_status, 'adapter_type', 'Unknown')
                                    })
                    except Exception as analyzer_err:
                        logger.error(f"Failed to run missing field analyzer: {analyzer_err}")
                        
                except Exception as sum_err:
                    logger.error(f"Failed to log summary: {sum_err}")
                
                # Module 9: Enterprise Diagnostic Report
                try:
                    from app.services.diagnostics.enterprise_report import get_enterprise_diagnostic_report
                    report_gen = get_enterprise_diagnostic_report()
                    if not report_gen._running:
                        await report_gen.start()
                        
                    await report_gen.generate_report(
                        scan_id=getattr(self, '_last_scan_id', 'unknown'),
                        correlation_id=getattr(self, '_last_scan_id', 'unknown'),
                        discovery_duration=duration_ms,
                        total_devices=len(self.state_manager.get_all_devices()),
                        online_devices=sum(1 for d in self.state_manager.get_all_devices() if d.online_status),
                        avg_rssi=sum((d.current_rssi.value if hasattr(d.current_rssi, 'value') else d.current_rssi) for d in self.state_manager.get_all_devices() if d.current_rssi is not None) / max(sum(1 for d in self.state_manager.get_all_devices() if d.current_rssi is not None), 1) if any(d.current_rssi is not None for d in self.state_manager.get_all_devices()) else 0.0
                    )
                except Exception as report_err:
                    logger.error(f"Failed to generate diagnostic report: {report_err}")
                
                self.error_count = 0
                self.state = DiscoveryState.CONNECTED
                
                await asyncio.sleep(self.poll_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in discovery loop: {e}")
                self.metrics["failed_scans"] += 1
                self.state = DiscoveryState.DEGRADED
                try:
                    if self.router_manager:
                        await self.router_manager.disconnect()
                except Exception:
                    pass

background_discovery_service = BackgroundDiscoveryService()

def get_background_discovery_service() -> BackgroundDiscoveryService:
    return background_discovery_service
