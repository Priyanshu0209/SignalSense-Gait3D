import logging
import asyncio
import re
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.adapters.router.base import RouterAdapter
from app.schemas.router import RouterStatus, ConnectedDevice, RouterCapabilities

logger = logging.getLogger("signalsense.adapters.linux_wifi")

class LinuxWiFiAdapter(RouterAdapter):

    def __init__(self, host: str, username: str, password: str, options: Dict[str, Any] = None):
        super().__init__(host, username, password, options)
        self.interface = None
        self.use_nmcli = False
        self._connected = False
        
    async def _run_command(self, *args) -> tuple[bool, str]:
        try:
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                return True, stdout.decode('utf-8').strip()
            return False, stderr.decode('utf-8').strip()
        except FileNotFoundError:
            return False, "Command not found"
        except Exception as e:
            return False, str(e)

    async def _detect_interface(self) -> Optional[str]:
        # Try `iw dev` first to find a managed interface
        success, output = await self._run_command('iw', 'dev')
        if success:
            current_iface = None
            for line in output.split('\n'):
                line = line.strip()
                if line.startswith('Interface '):
                    current_iface = line.split()[1]
                elif line.startswith('type managed') and current_iface:
                    return current_iface
                    
        # Fallback to nmcli
        success, output = await self._run_command('nmcli', '-t', '-f', 'DEVICE,TYPE,STATE', 'device')
        if success:
            for line in output.split('\n'):
                parts = line.split(':')
                if len(parts) == 3:
                    dev, dtype, state = parts
                    if dtype == 'wifi' and state == 'connected':
                        return dev
                        
        return None

    async def connect(self) -> bool:

        self.interface = await self._detect_interface()
        
        if not self.interface:
            logger.warning("[LinuxWiFi] No managed wireless interface found or connected.")
            return False
            
        logger.info(f"[LinuxWiFi] Detected interface: {self.interface}")
        
        # Check if iw works for link
        success, output = await self._run_command('iw', 'dev', self.interface, 'link')
        if success and "Not connected" not in output:
            self._connected = True
            return True
            
        # Fallback to nmcli
        success, output = await self._run_command('nmcli', '-t', '-f', 'ACTIVE', 'dev', 'wifi')
        if success and 'yes' in output:
            self._connected = True
            self.use_nmcli = True
            return True
            
        return False

    async def disconnect(self) -> None:
        self._connected = False
        self.interface = None

    def get_capabilities(self) -> RouterCapabilities:
        return RouterCapabilities(
            supports_rssi=True,
            supports_clients=False,
            supports_cpu=False,
            supports_memory=False,
            supports_channels=True,
            supports_tx_rate=True,
            supports_rx_rate=True,
            supports_hostname=False,
            supports_vendor=False,
            supports_firmware=False
        )

    async def get_status(self) -> RouterStatus:
        # We don't have true router status, just fake a minimal one
        return RouterStatus(
            router_name="Local WiFi Interface",
            router_model="Linux Wireless",
            vendor="Generic",
            firmware_version="N/A",
            gateway_ip=self.host,
            mac_address="Unknown",
            connection_type="wifi",
            cpu_usage=None,
            memory_usage=None,
            network_status="active" if self._connected else "inactive",
            internet_status="unknown",
            uptime_seconds=0,
            connected_devices_count=1,
            timestamp=datetime.now(timezone.utc).isoformat(),
            capabilities=self.get_capabilities().dict()
        )

    async def _parse_iw_link(self) -> Optional[Dict[str, Any]]:
        success, output = await self._run_command('iw', 'dev', self.interface, 'link')
        if not success or "Not connected" in output:
            return None
            
        data = {
            "source": "linux",
            "interface": self.interface,
            "bssid": "Unknown",
            "ssid": "Unknown",
            "frequency_mhz": None,
            "signal_dbm": None,
            "rx_bitrate_mbps": None,
            "tx_bitrate_mbps": None
        }
        
        for line in output.split('\n'):
            line = line.strip()
            if line.startswith("Connected to"):
                data["bssid"] = line.split(" ")[2].upper()
            elif line.startswith("SSID:"):
                data["ssid"] = line.split(":", 1)[1].strip()
                logger.info(f"[LinuxWiFi] SSID: {data['ssid']}")
            elif line.startswith("freq:"):
                try:
                    data["frequency_mhz"] = int(float(line.split(" ")[1]))
                    logger.info(f"[LinuxWiFi] Frequency: {data['frequency_mhz']} MHz")
                except ValueError:
                    pass
            elif line.startswith("signal:"):
                try:
                    data["signal_dbm"] = int(line.split(" ")[1])
                    logger.info(f"[LinuxWiFi] RSSI: {data['signal_dbm']} dBm")
                except ValueError:
                    pass
            elif line.startswith("rx bitrate:"):
                try:
                    data["rx_bitrate_mbps"] = float(line.split(" ")[2])
                except ValueError:
                    pass
            elif line.startswith("tx bitrate:"):
                try:
                    data["tx_bitrate_mbps"] = float(line.split(" ")[2])
                except ValueError:
                    pass
                    
        return data

    async def _parse_nmcli(self) -> Optional[Dict[str, Any]]:
        # nmcli -t -f active,ssid,bssid,signal,freq dev wifi
        success, output = await self._run_command('nmcli', '-t', '-f', 'active,ssid,bssid,signal,freq', 'dev', 'wifi')
        if not success:
            return None
            
        for line in output.split('\n'):
            if line.startswith('yes:'):
                parts = [x.replace(r'\:', ':') for x in re.split(r'(?<!\\):', line)]
                if len(parts) >= 5:
                    ssid = parts[1]
                    bssid = parts[2].upper()
                    signal_quality = parts[3]
                    freq_str = parts[4].replace(' MHz', '').strip()
                    
                    # Convert 0-100 quality to approx dBm: quality = 2 * (dBm + 100) -> dBm = (quality / 2) - 100
                    try:
                        qual = int(signal_quality)
                        dbm = (qual / 2) - 100
                    except ValueError:
                        dbm = None
                        
                    logger.info(f"[LinuxWiFi] SSID: {ssid}")
                    if freq_str.isdigit():
                        logger.info(f"[LinuxWiFi] Frequency: {freq_str} MHz")
                    if dbm is not None:
                        logger.info(f"[LinuxWiFi] RSSI: {int(dbm)} dBm")
                        
                    return {
                        "source": "linux",
                        "interface": self.interface,
                        "bssid": bssid,
                        "ssid": ssid,
                        "frequency_mhz": int(freq_str) if freq_str.isdigit() else None,
                        "signal_dbm": int(dbm) if dbm is not None else None,
                        "rx_bitrate_mbps": None,
                        "tx_bitrate_mbps": None
                    }
        return None

    async def get_connected_devices(self) -> List[ConnectedDevice]:
        if not self._connected or not self.interface:
            return []
            
        data = None
        if not self.use_nmcli:
            data = await self._parse_iw_link()
            if not data:
                logger.info("[LinuxWiFi] iw failed to provide link data. Attempting nmcli fallback.")
                data = await self._parse_nmcli()
        else:
            data = await self._parse_nmcli()
            
        if not data or data["signal_dbm"] is None:
            logger.info("[LinuxWiFi] RSSI unavailable")
            return []
            
        # The BSSID is the gateway router MAC in this context
        return [ConnectedDevice(
            mac_address=data["bssid"],
            ip_address=self.host, # Gateway IP
            hostname="Gateway",
            rssi=data["signal_dbm"],
            signal_quality=None,
            connection_state="active",
            device_type="Router",
            manufacturer="Unknown",
            last_seen=datetime.now(timezone.utc).isoformat(),
            connection_duration_seconds=0,
            tx_rate=data["tx_bitrate_mbps"],
            rx_rate=data["rx_bitrate_mbps"]
        )]
