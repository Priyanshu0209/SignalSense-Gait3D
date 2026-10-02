from abc import ABC, abstractmethod
from typing import List, Dict, Any
from app.schemas.router import RouterStatus, ConnectedDevice, RouterCapabilities

class RouterAdapter(ABC):

    def __init__(self, host: str, username: str, password: str, options: Dict[str, Any] = None):
        self.host = host
        self.username = username
        self.password = password
        self.options = options or {}
        
    @abstractmethod
    async def connect(self) -> bool:

        pass
        
    @abstractmethod
    async def disconnect(self) -> None:

        pass
        
    @abstractmethod
    def get_capabilities(self) -> RouterCapabilities:

        pass
        
    @abstractmethod
    async def get_status(self) -> RouterStatus:

        pass
        
    @abstractmethod
    async def get_connected_devices(self) -> List[ConnectedDevice]:

        pass
