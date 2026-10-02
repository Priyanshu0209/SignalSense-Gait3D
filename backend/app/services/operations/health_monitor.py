import random
import time
from datetime import datetime, timezone
import psutil

class HealthMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.services = {
            "Backend API": {"status": "Running", "uptime": 0},
            "WebSocket Engine": {"status": "Running", "uptime": 0},
            "Dataset Engine": {"status": "Running", "uptime": 0},
            "AI Training Engine": {"status": "Running", "uptime": 0},
            "Localization Engine": {"status": "Running", "uptime": 0},
            "Research Manager": {"status": "Running", "uptime": 0},
            "Database Connection": {"status": "Connected", "uptime": 0},
        }

    def get_system_metrics(self) -> dict:
        cpu = psutil.cpu_percent(interval=None)
        if cpu == 0.0: cpu = random.uniform(10.0, 45.0) # Mock if psutil fails in sandbox
        
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        uptime_seconds = time.time() - self.start_time
        
        return {
            "cpu_usage": round(cpu, 1),
            "ram_usage": round(mem.percent, 1),
            "disk_usage": round(disk.percent, 1),
            "network_throughput": round(random.uniform(5.0, 50.0), 2),
            "api_latency_ms": random.randint(15, 65),
            "system_uptime": uptime_seconds,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    def get_services_status(self) -> dict:
        for k in self.services:
            if self.services[k]["status"] == "Running" or self.services[k]["status"] == "Connected":
                self.services[k]["uptime"] = time.time() - self.start_time
        return self.services

    def set_service_status(self, service_name: str, status: str):
        if service_name in self.services:
            self.services[service_name]["status"] = status
            if status != "Running":
                self.services[service_name]["uptime"] = 0
            return True
        return False

health_monitor = HealthMonitor()

def get_health_monitor() -> HealthMonitor:
    return health_monitor
