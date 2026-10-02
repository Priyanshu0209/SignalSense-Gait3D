import logging
import asyncio
from typing import Optional, List
from app.adapters.router.base import RouterAdapter
from app.adapters.router.factory import RouterFactory
from app.schemas.router import RouterStatus, ConnectedDevice
from app.utils.auto_discovery import get_default_gateway
from app.core.config import settings

logger = logging.getLogger("signalsense.manager.router")

class RouterManager:

    def __init__(self, adapter_type: str, host: str, username: str, password: str, options: dict = None):
        self.preferred_adapter_type = adapter_type
        self.host = host
        self.username = username
        self.password = password
        self.options = options
        self.adapter: Optional[RouterAdapter] = None
        self.is_connecting = False
        
    async def connect(self) -> bool:

        if self.is_connecting:
            return False
            
        self.is_connecting = True
        try:
            if self.host.lower() == "auto":
                logger.info("Auto-discovering router IP...")
                self.host = get_default_gateway()

            adapter_priorities = []
            if self.preferred_adapter_type and self.preferred_adapter_type.lower() != "auto":
                adapter_priorities.append(self.preferred_adapter_type.lower())
                
            default_types = ["ssh", "snmp", "rest", "netgear", "linux", "passive"]
                
            for default_type in default_types:
                if default_type not in adapter_priorities:
                    adapter_priorities.append(default_type)
            
            logger.info(f"Smart connection sequence: {adapter_priorities} on host {self.host}")
            
            name_map = {
                "ssh": "SSH Adapter",
                "snmp": "SNMP Adapter",
                "rest": "REST Adapter",
                "linux": "Linux WiFi Adapter",
                "passive": "Passive Discovery",
                "mock": "Mock Adapter",
                "vendor": "Vendor Adapter",
                "netgear": "NETGEAR Router Adapter"
            }
            fail_msg_map = {
                "ssh": "SSH authentication failed.",
                "snmp": "SNMP unavailable.",
                "rest": "REST unavailable.",
                "linux": "Linux WiFi unavailable or not connected.",
                "passive": "Passive Discovery failed.",
                "mock": "Mock Adapter failed.",
                "vendor": "Vendor API unavailable.",
                "netgear": "NETGEAR Authentication or Web UI unavailable."
            }

            for adapter_type in adapter_priorities:
                friendly_name = name_map.get(adapter_type, f"{adapter_type} Adapter")
                fail_msg = fail_msg_map.get(adapter_type, f"{friendly_name} unavailable.")
                
                try:
                    logger.info(f"Trying {friendly_name}...")
                    adapter = RouterFactory.create_adapter(
                        adapter_type=adapter_type,
                        host=self.host,
                        username=self.username,
                        password=self.password,
                        options=self.options
                    )
                    
                    if await adapter.connect():
                        self.adapter = adapter
                        if adapter_type == "passive":
                            logger.info("Passive Discovery initialized successfully.")
                            logger.info("Discovery completed.")
                        else:
                            logger.info(f"{friendly_name} initialized successfully.")
                            
                        logger.info("Selected Adapter:")
                        logger.info(friendly_name)
                        return True
                    else:
                        logger.info(fail_msg)
                except Exception as e:
                    logger.info(fail_msg)
                    logger.debug(f"Error details for {adapter_type}: {e}")
                    
            logger.error("All adapter connection attempts failed.")
            self.adapter = None
            return False
        finally:
            self.is_connecting = False
        
    async def disconnect(self) -> None:

        if self.adapter:
            logger.info("Disconnecting from router...")
            try:
                await self.adapter.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.adapter = None
        
    async def get_status(self) -> Optional[RouterStatus]:

        if not self.adapter: 
            return None
        try:
            return await self.adapter.get_status()
        except Exception as e:
            logger.error(f"Failed to get router status: {e}")
            return None
            
    async def get_connected_devices(self) -> List[ConnectedDevice]:

        if not self.adapter: 
            return []
        try:
            devices = await self.adapter.get_connected_devices()
            logger.info(f"[DEBUG LOG: ROUTER DISCOVERY] Adapter ({self.adapter.__class__.__name__}) discovered exactly {len(devices)} connected Wi-Fi device(s).")
            from app.services.diagnostics.diagnostics_logger import get_diagnostics_logger
            logger_service = get_diagnostics_logger()
            for dev in devices:
                rssi_val = getattr(dev, 'rssi', getattr(dev, 'current_rssi', None))
                logger.info(f"  [ROUTER DEVICE LOG] MAC: {dev.mac_address} | IP: {dev.ip_address} | Hostname: {dev.hostname or 'N/A'} | RSSI: {rssi_val} dBm | Timestamp: {dev.last_seen}")
                logger_service.log_router_layer(
                    dev.mac_address, 
                    rssi_val,
                    f"Adapter: {self.adapter.__class__.__name__}"
                )
            return devices
        except Exception as e:
            logger.error(f"Failed to get connected devices: {e}")
            return []

    async def get_diagnostics(self) -> dict:

        diag = {}
        if not self.adapter:
            diag["error"] = "No adapter initialized"
        elif hasattr(self.adapter, 'diagnostics'):
            if callable(self.adapter.diagnostics):
                import asyncio
                if asyncio.iscoroutinefunction(self.adapter.diagnostics):
                    diag = await self.adapter.diagnostics()
                else:
                    diag = self.adapter.diagnostics()
            else:
                diag = self.adapter.diagnostics
        else:
            diag["error"] = "Diagnostics not supported by current adapter"
            
        # Enrich with Background Discovery Service metrics
        try:
            from app.collectors.data_collector import get_background_discovery_service
            bds = get_background_discovery_service()
            diag["background_service"] = {
                "state": bds.state.value if hasattr(bds.state, "value") else str(bds.state),
                "db_queue_size": bds.db_queue.qsize(),
                "ws_queue_size": bds.ws_queue.qsize(),
                "metrics": bds.metrics
            }
        except ImportError:
            pass
            
        return diag

# Singleton instance to be initialized in main or dependency injection
router_manager: Optional[RouterManager] = None

def get_router_manager() -> RouterManager:
    if not router_manager:
        raise RuntimeError("RouterManager has not been initialized.")
    return router_manager
