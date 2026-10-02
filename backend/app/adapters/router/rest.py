import httpx
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.adapters.router.base import RouterAdapter
from app.schemas.router import RouterStatus, ConnectedDevice, RouterCapabilities

logger = logging.getLogger("signalsense.adapters.rest")

class RESTRouterAdapter(RouterAdapter):

    def __init__(self, host: str, username: str, password: str, options: Dict[str, Any] = None):
        super().__init__(host, username, password, options)
        self.base_url = f"http://{self.host}/api"
        self.client: Optional[httpx.AsyncClient] = None
        self._auth_token: Optional[str] = None
        
    async def connect(self) -> bool:
        try:
            self.client = httpx.AsyncClient(verify=False)
            
            # Example authentication payload
            payload = {
                "username": self.username,
                "password": self.password
            }
            
            # This is a placeholder endpoint and requires adaptation per router vendor
            # response = await self.client.post(f"{self.base_url}/login", json=payload)
            # response.raise_for_status()
            # self._auth_token = response.json().get("token")
            
            # Since this is a placeholder, we return False to simulate unavailability
            # logger.info(f"Successfully connected to REST API router at {self.host}")
            return False
        except Exception as e:
            logger.error(f"Failed to connect to REST API router at {self.host}: {e}")
            if self.client:
                await self.client.aclose()
                self.client = None
            return False

    async def disconnect(self) -> None:
        if self.client:
            # Optionally send logout request
            await self.client.aclose()
            self.client = None
            logger.info(f"Disconnected from REST API router at {self.host}")

    def get_capabilities(self) -> RouterCapabilities:
        return RouterCapabilities(
            supports_rssi=True,
            supports_clients=True,
            supports_cpu=False,
            supports_memory=False,
            supports_channels=False,
            supports_tx_rate=False,
            supports_rx_rate=False,
            supports_hostname=True,
            supports_vendor=False,
            supports_firmware=True
        )

    async def get_status(self) -> RouterStatus:
        if not self.client:
            raise ConnectionError("REST client not initialized.")
            
        try:
            # Example request
            # response = await self.client.get(f"{self.base_url}/status", headers={"Authorization": f"Bearer {self._auth_token}"})
            # data = response.json()
            
            now = datetime.now(timezone.utc)
            return RouterStatus(
                router_name="REST-Router",
                router_model="Unknown (REST)",
                firmware_version="API based",
                cpu_usage=0.0,
                memory_usage=0.0,
                network_status="online",
                internet_status="unknown",
                uptime_seconds=0,
                connected_devices_count=0,
                timestamp=now,
                capabilities=self.get_capabilities()
            )
        except Exception as e:
            logger.error(f"Error fetching status from REST router: {e}")
            raise

    async def get_connected_devices(self) -> List[ConnectedDevice]:
        if not self.client:
            raise ConnectionError("REST client not initialized.")
            
        devices = []
        try:
            # Example request
            # response = await self.client.get(f"{self.base_url}/devices", headers={"Authorization": f"Bearer {self._auth_token}"})
            # for item in response.json():
            #     devices.append(ConnectedDevice(...))
            return devices
        except Exception as e:
            logger.error(f"Error fetching connected devices from REST router: {e}")
            raise
