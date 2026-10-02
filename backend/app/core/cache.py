import asyncio
import time
from collections import OrderedDict
from typing import Any, Optional, Dict

class QueryCache:

    def __init__(self, max_size: int = 1000, default_ttl_seconds: int = 60):
        self.max_size = max_size
        self.default_ttl = default_ttl_seconds
        self._cache: OrderedDict = OrderedDict()
        self._lock = asyncio.Lock()
        
        # Diagnostics
        self.hits = 0
        self.misses = 0
        self.evictions = 0

    async def get(self, key: str) -> Optional[Any]:
        async with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
                
            entry = self._cache[key]
            
            # Check TTL
            if time.time() > entry['expiry']:
                del self._cache[key]
                self.misses += 1
                self.evictions += 1
                return None
                
            # Move to end (mark as recently used)
            self._cache.move_to_end(key)
            self.hits += 1
            return entry['value']

    async def set(self, key: str, value: Any, ttl_seconds: Optional[int] = None):
        ttl = ttl_seconds if ttl_seconds is not None else self.default_ttl
        expiry = time.time() + ttl
        
        async with self._lock:
            if key in self._cache:
                self._cache.move_to_end(key)
            self._cache[key] = {'value': value, 'expiry': expiry}
            
            # Enforce capacity
            while len(self._cache) > self.max_size:
                self._cache.popitem(last=False)
                self.evictions += 1

    async def invalidate(self, key: str):
        async with self._lock:
            if key in self._cache:
                del self._cache[key]

    async def clear(self):
        async with self._lock:
            self._cache.clear()
            
    async def get_diagnostics(self) -> Dict[str, Any]:
        async with self._lock:
            total_requests = self.hits + self.misses
            hit_ratio = (self.hits / total_requests) if total_requests > 0 else 0.0
            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "hits": self.hits,
                "misses": self.misses,
                "evictions": self.evictions,
                "hit_ratio": round(hit_ratio, 2)
            }
