import platform
import subprocess
import socket
import logging
from typing import Dict, Optional
import re

try:
    import netifaces
    HAS_NETIFACES = True
except ImportError:
    HAS_NETIFACES = False

logger = logging.getLogger("signalsense.auto_discovery")

def get_default_gateway_and_interface() -> tuple[Optional[str], Optional[str]]:
    # Priority 1: ip route
    try:
        out = subprocess.check_output(["ip", "route"]).decode()
        for line in out.splitlines():
            if line.startswith("default"):
                parts = line.split()
                try:
                    gw_idx = parts.index("via")
                    dev_idx = parts.index("dev")
                    return parts[gw_idx + 1], parts[dev_idx + 1]
                except ValueError:
                    pass
    except Exception:
        pass

    # Priority 2: route -n
    try:
        out = subprocess.check_output(["route", "-n"]).decode()
        for line in out.splitlines():
            if line.startswith("0.0.0.0"):
                parts = line.split()
                if len(parts) >= 8:
                    return parts[1], parts[-1]
    except Exception:
        pass

    # Priority 3: netstat -rn
    try:
        out = subprocess.check_output(["netstat", "-rn"]).decode()
        for line in out.splitlines():
            if line.startswith("0.0.0.0") or line.startswith("default"):
                parts = line.split()
                if len(parts) >= 6:
                    return parts[1], parts[-1]
    except Exception:
        pass
        
    return None, None

def get_default_gateway() -> Optional[str]:
    gw, _ = get_default_gateway_and_interface()
    return gw

def get_local_ip() -> Optional[str]:
    # Priority 1: hostname -I
    try:
        out = subprocess.check_output(["hostname", "-I"]).decode().strip()
        if out:
            # First IP is usually the primary one
            return out.split()[0]
    except Exception:
        pass
        
    # Priority 2: ip addr
    try:
        out = subprocess.check_output(["ip", "addr"]).decode()
        # Find first non-loopback inet
        for line in out.splitlines():
            line = line.strip()
            if line.startswith("inet ") and "127.0.0.1" not in line:
                ip = line.split()[1].split("/")[0]
                return ip
    except Exception:
        pass
        
    # Priority 3: socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        s.close()
        return IP
    except Exception:
        pass
        
    return None

def get_active_network_info() -> Dict[str, Optional[str]]:
    info = {
        "gateway_ip": None,
        "local_ip": get_local_ip(),
        "interface": None,
        "ssid": None,
        "bssid": None,
        "dns": None,
        "subnet": None
    }
    
    gw, iface = get_default_gateway_and_interface()
    info["gateway_ip"] = gw
    info["interface"] = iface
    
    # Try getting Subnet
    if HAS_NETIFACES and iface != "unknown":
        try:
            addrs = netifaces.ifaddresses(iface)
            if netifaces.AF_INET in addrs:
                info["subnet"] = addrs[netifaces.AF_INET][0].get('netmask')
        except Exception:
            pass
            
    # Try getting DNS (Linux/macOS)
    if platform.system() != "Windows":
        try:
            with open("/etc/resolv.conf", "r") as f:
                for line in f:
                    if line.startswith("nameserver"):
                        info["dns"] = line.split()[1]
                        break
        except Exception:
            pass

    # Try getting SSID/BSSID using iwgetid / iwconfig
    if platform.system() == "Linux":
        try:
            ssid = subprocess.check_output(["iwgetid", "-r"]).decode().strip()
            if ssid:
                info["ssid"] = ssid
            bssid = subprocess.check_output(["iwgetid", "-a", "-r"]).decode().strip()
            if bssid:
                info["bssid"] = bssid
        except Exception:
            pass
            
        if not info["ssid"]:
            try:
                out = subprocess.check_output(["nmcli", "-t", "-f", "active,ssid,bssid", "dev", "wifi"]).decode()
                for line in out.splitlines():
                    if line.startswith("yes:"):
                        parts = line.split(":")
                        if len(parts) >= 3:
                            info["ssid"] = parts[1]
                            info["bssid"] = ":".join(parts[2:])
                        break
            except Exception:
                pass

    return info
