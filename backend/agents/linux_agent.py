import time
import requests
import psutil
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linux_agent")

class LinuxHostAgent:
    """
    Standalone agent to collect CPU, RAM, Temp, Network stats from a Linux host
    and push them to the SignalSense Remote Ingestion API.
    """
    
    def __init__(self, endpoint_url: str, agent_id: str = "linux_edge_01"):
        self.endpoint_url = endpoint_url
        self.agent_id = agent_id
        
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect host telemetry."""
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        net = psutil.net_io_counters()
        
        # In a real environment, sensors_temperatures() would be used for temp
        temp = 45.0
        try:
            temps = psutil.sensors_temperatures()
            if temps and 'coretemp' in temps:
                temp = temps['coretemp'][0].current
        except Exception:
            pass
            
        return {
            "cpu_usage": cpu,
            "ram_usage": mem.percent,
            "disk_usage": disk.percent,
            "temperature_c": temp,
            "net_bytes_sent": net.bytes_sent,
            "net_bytes_recv": net.bytes_recv
        }
        
    def push_telemetry(self):
        """Infinite loop pushing data to SignalSense."""
        logger.info(f"Starting Linux Host Agent: {self.agent_id}")
        while True:
            try:
                metrics = self.collect_metrics()
                payload = {
                    "source_id": self.agent_id,
                    "topic": "telemetry.agent.host",
                    "data": metrics
                }
                
                resp = requests.post(
                    f"{self.endpoint_url}/telemetry", 
                    json=payload,
                    timeout=5
                )
                if resp.status_code == 200:
                    logger.info(f"Pushed telemetry successfully. CPU: {metrics['cpu_usage']}%")
                else:
                    logger.error(f"Failed to push telemetry: HTTP {resp.status_code}")
                    
            except Exception as e:
                logger.error(f"Connection error: {e}")
                
            time.sleep(10)

if __name__ == "__main__":
    # Example usage
    agent = LinuxHostAgent(endpoint_url="http://localhost:8000/api/v1/ingest")
    agent.push_telemetry()
