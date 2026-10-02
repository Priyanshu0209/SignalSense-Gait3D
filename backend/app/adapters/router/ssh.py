import asyncio
import asyncssh
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from app.adapters.router.base import RouterAdapter
from app.schemas.router import RouterStatus, ConnectedDevice, RouterCapabilities

logger = logging.getLogger("signalsense.adapters.ssh")

class SSHRouterAdapter(RouterAdapter):

    def __init__(self, host: str, username: str, password: str, options: Dict[str, Any] = None):
        super().__init__(host, username, password, options)
        self.connection: Optional[asyncssh.SSHClientConnection] = None
        self._start_time = datetime.now(timezone.utc)
        self._prev_idle = 0
        self._prev_total = 0
        
    async def connect(self) -> bool:
        try:
            self.connection = await asyncssh.connect(
                self.host,
                username=self.username,
                password=self.password,
                known_hosts=None
            )
            logger.info(f"Successfully connected to SSH router at {self.host}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to SSH router at {self.host}: {e}")
            return False

    async def disconnect(self) -> None:
        if self.connection:
            self.connection.close()
            await self.connection.wait_closed()
            self.connection = None
            logger.info(f"Disconnected from SSH router at {self.host}")

    async def _execute_command(self, command: str) -> str:
        if not self.connection:
            raise ConnectionError("SSH connection not established.")
        
        result = await self.connection.run(command, check=False)
        if result.exit_status != 0:
            logger.debug(f"Command '{command}' failed with status {result.exit_status}")
            return ""
        return result.stdout.strip() if result.stdout else ""

    def get_capabilities(self) -> RouterCapabilities:
        return RouterCapabilities(
            supports_rssi=False,
            supports_clients=True,
            supports_cpu=True,
            supports_memory=True,
            supports_channels=False,
            supports_tx_rate=False,
            supports_rx_rate=False,
            supports_hostname=True,
            supports_vendor=False,
            supports_firmware=True
        )

    async def get_status(self) -> RouterStatus:

        if not self.connection:
            raise ConnectionError("SSH connection not established.")
            
        try:
            uptime_str = await self._execute_command("cat /proc/uptime | awk '{print $1}'")
            uptime = int(float(uptime_str)) if uptime_str else 0
            
            # CPU Usage
            stat_str = await self._execute_command("cat /proc/stat | grep '^cpu '")
            cpu_usage = 0.0
            if stat_str:
                parts = stat_str.split()
                if len(parts) >= 5:
                    idle = float(parts[4])
                    total = sum(float(x) for x in parts[1:])
                    if self._prev_total > 0:
                        idle_delta = idle - self._prev_idle
                        total_delta = total - self._prev_total
                        if total_delta > 0:
                            cpu_usage = 100.0 * (1.0 - idle_delta / total_delta)
                    self._prev_idle = idle
                    self._prev_total = total
            
            # Memory Usage
            mem_str = await self._execute_command("cat /proc/meminfo")
            mem_usage = 0.0
            mem_total = 1
            mem_free = 0
            if mem_str:
                for line in mem_str.splitlines():
                    if line.startswith("MemTotal:"):
                        mem_total = int(line.split()[1])
                    elif line.startswith("MemAvailable:") or line.startswith("MemFree:"):
                        mem_free = int(line.split()[1])
                mem_usage = 100.0 * (1.0 - (mem_free / mem_total)) if mem_total > 0 else 0.0
            
            uname_str = await self._execute_command("uname -r")
            
            # Get number of devices
            arp_str = await self._execute_command("arp -a")
            dev_count = len(arp_str.splitlines()) if arp_str else 0
            
            now = datetime.now(timezone.utc)
            
            return RouterStatus(
                router_name="Linux Router",
                router_model="Generic SSH",
                firmware_version=uname_str[:20] if uname_str else "Unknown",
                vendor="Generic",
                cpu_usage=round(cpu_usage, 2),
                memory_usage=round(mem_usage, 2),
                network_status="online",
                internet_status="connected",
                uptime_seconds=uptime,
                connected_devices_count=dev_count,
                timestamp=now,
                adapter_type="SSH Adapter",
                connection_status="Connected",
                capabilities=self.get_capabilities()
            )
        except Exception as e:
            logger.error(f"Error fetching status from SSH router: {e}")
            raise

    async def get_connected_devices(self) -> List[ConnectedDevice]:

        if not self.connection:
            raise ConnectionError("SSH connection not established.")
            
        devices = []
        try:
            # We use 'ip neigh' as it's common on Linux
            neigh_str = await self._execute_command("ip neigh show")
            now = datetime.now(timezone.utc)
            
            if neigh_str:
                for line in neigh_str.splitlines():
                    parts = line.split()
                    if len(parts) >= 5 and ("REACHABLE" in line or "STALE" in line or "DELAY" in line):
                        ip = parts[0]
                        mac = parts[4]
                        
                        devices.append(ConnectedDevice(
                            mac_address=mac.upper(),
                            ip_address=ip,
                            hostname=f"Device-{ip.split('.')[-1]}",
                            rssi=None,
                            signal_quality=None,
                            connection_state="connected",
                            device_type="Unknown",
                            manufacturer="Unknown",
                            last_seen=now,
                            connection_duration_seconds=0,
                            tx_rate=0.0,
                            rx_rate=0.0
                        ))
            return devices
        except Exception as e:
            logger.error(f"Error fetching connected devices from SSH router: {e}")
            raise
