import asyncio
import logging
import time
import socket
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.adapters.router.base import RouterAdapter
from app.schemas.router import RouterStatus, ConnectedDevice, RouterCapabilities
from app.utils.auto_discovery import get_default_gateway_and_interface, get_local_ip

logger = logging.getLogger("signalsense.adapters.passive")

class PassiveDiscoveryAdapter(RouterAdapter):

    def __init__(self, host: str, username: str, password: str, options: Dict[str, Any] = None):
        super().__init__(host, username, password, options)
        self.is_connected = False
        self._cached_devices = []
        self._last_scan_time = 0.0
        self._cache_ttl = 30  # seconds
        self._discovery_duration = 0.0
        self._gateway_mac = "00:00:00:00:00:00"
        self._interface = "unknown"
        self._local_ip = "unknown"
        
        self._vendor_cache = {
            "00:50:56": "VMware",
            "08:00:27": "Oracle",
            "DC:A6:32": "Raspberry Pi",
            "B8:27:EB": "Raspberry Pi",
            "00:14:22": "Dell",
            "00:1A:11": "Google",
            "3C:5A:B4": "Google",
            "F4:F5:E8": "Google",
            "48:4B:AA": "Apple",
            "A4:5E:60": "Apple",
            "00:1A:A0": "Dell",
            "E4:5F:01": "Raspberry Pi",
            "18:C0:4D": "Sony",
            "00:24:E4": "Cisco",
            "28:6D:97": "Samsung",
            "50:C7:BF": "TP-Link",
            "E0:D5:5E": "TP-Link",
            "C4:6E:1F": "TP-Link",
            "00:11:32": "Synology",
        }
        
    async def connect(self) -> bool:
        try:
            logger.info("Initializing Passive Discovery Adapter...")
            
            gw, iface = get_default_gateway_and_interface()
            if gw:
                self.host = gw
            if iface:
                self._interface = iface
                
            local_ip = get_local_ip()
            if local_ip:
                self._local_ip = local_ip
                
            logger.info(f"Detected gateway: {self.host}")
            logger.info(f"Detected interface: {self._interface}")
            logger.info(f"Detected local IP: {self._local_ip}")
            
            await self._run_command(f"ping -c 1 -W 1 {self.host}")
            self.is_connected = True
            
            # Initial populate
            await self.get_connected_devices()
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize passive discovery: {e}")
            return False

    async def disconnect(self) -> None:
        self.is_connected = False
        logger.info("Closed Passive Discovery Adapter.")

    def get_capabilities(self) -> RouterCapabilities:
        return RouterCapabilities(
            supports_rssi=False,
            supports_clients=True,
            supports_cpu=False,
            supports_memory=False,
            supports_channels=False,
            supports_tx_rate=False,
            supports_rx_rate=False,
            supports_hostname=True,
            supports_vendor=True,
            supports_firmware=False
        )
        
    async def _resolve_vendor(self, mac: str) -> str:
        prefix = mac[:8].upper()
        if prefix in self._vendor_cache:
            return self._vendor_cache[prefix]
            
        try:
            import httpx
            async with httpx.AsyncClient(timeout=1.0) as client:
                response = await client.get(f"https://api.macvendors.com/{mac}")
                if response.status_code == 200:
                    vendor = response.text.strip()
                    self._vendor_cache[prefix] = vendor
                    logger.info(f"Vendor resolved: {vendor}")
                    return vendor
        except Exception:
            pass
            
        self._vendor_cache[prefix] = "Unknown"
        return "Unknown"
        
    async def _resolve_hostname(self, ip: str) -> str:
        try:
            # socket.gethostbyaddr blocks, we can run it in an executor if needed, 
            # but for a quick local DNS check, we will use it with try/except
            host = socket.gethostbyaddr(ip)
            return host[0]
        except Exception:
            return ""

    async def get_status(self) -> RouterStatus:
        if not self.is_connected:
            raise ConnectionError("Passive Adapter is not initialized.")
            
        now = datetime.now(timezone.utc)
        
        gw_vendor = await self._resolve_vendor(self._gateway_mac) if self._gateway_mac != "00:00:00:00:00:00" else "N/A"
        
        return RouterStatus(
            router_name="Passive Network Scan",
            router_model="N/A",
            firmware_version="N/A",
            vendor=gw_vendor,
            cpu_usage=None,
            memory_usage=None,
            network_status="online",
            internet_status="unknown",
            uptime_seconds=0,
            connected_devices_count=len(self._cached_devices),
            timestamp=now,
            adapter_type="Passive Discovery",
            connection_status="Active",
            gateway_ip=self.host,
            mac_address=self._gateway_mac,
            capabilities=self.get_capabilities()
        )

    async def get_connected_devices(self) -> List[ConnectedDevice]:
        if not self.is_connected:
            raise ConnectionError("Passive Adapter is not initialized.")
            
        current_time = time.time()
        if current_time - self._last_scan_time < self._cache_ttl and self._cached_devices:
            return self._cached_devices
            
        start_time = time.time()
        devices = []
        try:
            output = await self._run_command("arp -a")
            now = datetime.now(timezone.utc)
            
            try:
                from app.services.diagnostics.raw_response_logger import get_raw_response_logger
                logger_service = get_raw_response_logger()
                logger_service.log_response(
                    router_ip=self.host,
                    gateway=self.host,
                    response_time_ms=(time.time() - start_time) * 1000,
                    discovery_duration_ms=0.0,
                    error_status=None,
                    raw_payload=output
                )
            except ImportError:
                pass
            
            if output:
                for line in output.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                        
                    ip = None
                    mac = None
                    hostname = "Unknown"
                    
                    if "at" in line and "(" in line and ")" in line:
                        parts = line.split()
                        try:
                            hostname_part = parts[0] if parts[0] != "?" else ""
                            ip_part = [p for p in parts if p.startswith("(") and p.endswith(")")][0]
                            ip = ip_part[1:-1]
                            
                            at_index = parts.index("at")
                            mac = parts[at_index + 1]
                            
                            if hostname_part and hostname_part != "?":
                                hostname = hostname_part
                        except Exception:
                            continue
                    elif len(line.split()) >= 3:
                        parts = line.split()
                        import re
                        if re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", parts[0]):
                            ip = parts[0]
                            mac = parts[1].replace("-", ":")
                            
                    if ip and mac and mac.count(":") == 5 and mac != "ff:ff:ff:ff:ff:ff":
                        mac = mac.upper()
                        
                        if ip == self.host:
                            self._gateway_mac = mac
                            logger.info(f"Detected gateway MAC: {mac}")
                        
                        if not mac.startswith("01:00:5E") and not mac.startswith("33:33:"):
                            vendor = await self._resolve_vendor(mac)
                            if hostname == "Unknown" or hostname == "":
                                resolved = await self._resolve_hostname(ip)
                                if resolved:
                                    hostname = resolved
                                elif vendor != "Unknown":
                                    hostname = f"{vendor}-{ip.split('.')[-1]}"
                                else:
                                    hostname = f"Device-{ip.split('.')[-1]}"
                            
                            devices.append(ConnectedDevice(
                                mac_address=mac,
                                ip_address=ip,
                                hostname=hostname,
                                rssi=None,
                                signal_quality=None,
                                connection_state="connected",
                                device_type="Unknown",
                                manufacturer=vendor,
                                last_seen=now,
                                connection_duration_seconds=0,
                                tx_rate=0.0,
                                rx_rate=0.0
                            ))
                            
            self._cached_devices = devices
            self._last_scan_time = current_time
            self._discovery_duration = (time.time() - start_time) * 1000
            
            logger.info(f"Devices discovered: {len(devices)}")
            logger.info(f"Discovery duration: {int(self._discovery_duration)} ms")
            
            return devices
        except Exception as e:
            logger.warning(f"Continuing discovery despite errors: {e}")
            return self._cached_devices

    async def _run_command(self, cmd: str) -> str:
        try:
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return stdout.decode('utf-8', errors='ignore')
            return ""
        except Exception as e:
            logger.debug(f"Command '{cmd}' failed: {e}")
            return ""

    @property
    def diagnostics(self) -> dict:
        return {
            "selected_adapter": "Passive Discovery",
            "gateway": self.host,
            "interface": getattr(self, '_interface', "unknown"),
            "discovery_duration_ms": int(getattr(self, '_discovery_duration', 0)),
            "connected_devices": len(getattr(self, '_cached_devices', [])),
            "capabilities": self.get_capabilities().model_dump() if hasattr(self.get_capabilities(), "model_dump") else {},
            "last_scan_age_seconds": int(time.time() - getattr(self, '_last_scan_time', 0)),
            "errors": []
        }
