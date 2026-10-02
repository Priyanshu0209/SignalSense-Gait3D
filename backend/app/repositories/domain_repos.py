from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.repositories.base import BaseRepository
from app.models.domain import (
    RouterModel, DeviceModel, DeviceSessionModel, RSSIHistoryModel,
    EventModel, AlertModel, SystemLogModel, SettingModel
)

class RouterRepository(BaseRepository[RouterModel]):
    def __init__(self):
        super().__init__(RouterModel)

class DeviceRepository(BaseRepository[DeviceModel]):
    def __init__(self):
        super().__init__(DeviceModel)
        
    async def get(self, db: AsyncSession, mac_address: str) -> Optional[DeviceModel]:
        result = await db.execute(select(self.model).filter(self.model.mac_address == mac_address))
        return result.scalars().first()

class DeviceSessionRepository(BaseRepository[DeviceSessionModel]):
    def __init__(self):
        super().__init__(DeviceSessionModel)

class RSSIRepository(BaseRepository[RSSIHistoryModel]):
    def __init__(self):
        super().__init__(RSSIHistoryModel)

class EventRepository(BaseRepository[EventModel]):
    def __init__(self):
        super().__init__(EventModel)

class AlertRepository(BaseRepository[AlertModel]):
    def __init__(self):
        super().__init__(AlertModel)

class SystemLogRepository(BaseRepository[SystemLogModel]):
    def __init__(self):
        super().__init__(SystemLogModel)

class SettingsRepository(BaseRepository[SettingModel]):
    def __init__(self):
        super().__init__(SettingModel)
        
    async def get(self, db: AsyncSession, key: str) -> Optional[SettingModel]:
        result = await db.execute(select(self.model).filter(self.model.key == key))
        return result.scalars().first()

# Global instances for the RepositoryManager
router_repo = RouterRepository()
device_repo = DeviceRepository()
session_repo = DeviceSessionRepository()
rssi_repo = RSSIRepository()
event_repo = EventRepository()
alert_repo = AlertRepository()
log_repo = SystemLogRepository()
settings_repo = SettingsRepository()
