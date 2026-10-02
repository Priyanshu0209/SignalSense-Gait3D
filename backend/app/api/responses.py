import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class ApiError(BaseModel):
    code: str
    message: str
    details: str

class StandardResponse(BaseModel):
    success: bool
    timestamp: str
    request_id: str
    version: str
    data: Any
    errors: List[ApiError]

def api_response(data: Any, success: bool = True, errors: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:

    return {
        "success": success,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_id": str(uuid.uuid4()),
        "version": "v1",
        "data": data,
        "errors": errors or []
    }
