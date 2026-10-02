from typing import Dict, Any
from app.adapters.router.base import RouterAdapter
from app.adapters.router.mock import MockRouterAdapter
from app.adapters.router.ssh import SSHRouterAdapter
from app.adapters.router.rest import RESTRouterAdapter
from app.adapters.router.snmp import SNMPRouterAdapter
from app.adapters.router.vendor import VendorRouterAdapter
from plugins.netgear.adapter import NetgearRouterAdapter
from app.adapters.router.passive import PassiveDiscoveryAdapter

class RouterFactory:

    @staticmethod
    def create_adapter(adapter_type: str, host: str, username: str, password: str, options: Dict[str, Any] = None) -> RouterAdapter:
        adapter_type = adapter_type.lower()
        
        if adapter_type == "mediatek_telnet":
            from app.adapters.router.mediatek_telnet import MediaTekTelnetAdapter
            return MediaTekTelnetAdapter(host, username, password, options)
        elif adapter_type == "mock":
            return MockRouterAdapter(host, username, password, options)
        elif adapter_type == "ssh":
            return SSHRouterAdapter(host, username, password, options)
        elif adapter_type == "rest":
            return RESTRouterAdapter(host, username, password, options)
        elif adapter_type == "snmp":
            return SNMPRouterAdapter(host, username, password, options)
        elif adapter_type == "vendor":
            return VendorRouterAdapter(host, username, password, options)
        elif adapter_type == "netgear":
            return NetgearRouterAdapter(host, username, password, options)
        elif adapter_type == "linux":
            from app.adapters.router.linux_wifi import LinuxWiFiAdapter
            return LinuxWiFiAdapter(host, username, password, options)
        elif adapter_type == "passive":
            return PassiveDiscoveryAdapter(host, username, password, options)
        else:
            raise ValueError(f"Unknown router adapter type: {adapter_type}")
