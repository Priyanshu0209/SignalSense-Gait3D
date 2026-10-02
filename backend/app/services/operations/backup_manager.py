import os
import uuid
import time
from datetime import datetime, timezone
import random

class BackupManager:
    def __init__(self):
        self.backups = []
        # Mock some existing backups
        for i in range(3):
            self.backups.append({
                "id": f"BAK-{uuid.uuid4().hex[:8].upper()}",
                "timestamp": (datetime.now().timestamp() - (i * 86400)), # Days ago
                "size_mb": random.randint(150, 500),
                "status": "Verified",
                "type": "Full System"
            })

    def get_backups(self):
        return sorted(self.backups, key=lambda x: x["timestamp"], reverse=True)

    def create_backup(self, backup_type: str = "Full System"):
        # Mocking backup creation
        time.sleep(2) # Simulate work
        new_backup = {
            "id": f"BAK-{uuid.uuid4().hex[:8].upper()}",
            "timestamp": datetime.now().timestamp(),
            "size_mb": random.randint(200, 600),
            "status": "Verified",
            "type": backup_type
        }
        self.backups.append(new_backup)
        return new_backup

    def restore_backup(self, backup_id: str):
        # Mocking restore
        time.sleep(3)
        return True

backup_manager = BackupManager()

def get_backup_manager() -> BackupManager:
    return backup_manager
