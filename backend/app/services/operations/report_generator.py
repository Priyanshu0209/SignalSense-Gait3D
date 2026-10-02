import os
from datetime import datetime
from app.services.operations.health_monitor import get_health_monitor
from app.services.operations.diagnostics_engine import get_diagnostics_engine

class ReportGenerator:
    def __init__(self):
        self.reports_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "docs"))
        os.makedirs(self.reports_dir, exist_ok=True)

    def generate_system_report(self) -> str:
        hm = get_health_monitor()
        sys_metrics = hm.get_system_metrics()
        services = hm.get_services_status()
        
        md = f"""# SignalSense Enterprise Operations Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Health
- **CPU Usage**: {sys_metrics['cpu_usage']}%
- **RAM Usage**: {sys_metrics['ram_usage']}%
- **Disk Usage**: {sys_metrics['disk_usage']}%
- **API Latency**: {sys_metrics['api_latency_ms']} ms

## Service Status
"""
        for srv, data in services.items():
            md += f"- **{srv}**: {data['status']} (Uptime: {data['uptime']:.1f}s)\n"
            
        md += "\n## Diagnostics\n"
        diag = get_diagnostics_engine().run_diagnostics()
        md += f"Status: {diag['status']}\n"
        for i in diag['issues_found']:
            md += f"- [{i['severity']}] {i['message']}\n"
            
        filename = f"OpsReport_{datetime.now().strftime('%Y%m%d%H%M')}.md"
        filepath = os.path.join(self.reports_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(md)
            
        return filepath

report_generator = ReportGenerator()

def get_report_generator() -> ReportGenerator:
    return report_generator
