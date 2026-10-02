from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import websocket_manager
import logging

logger = logging.getLogger("signalsense.api.ws")
router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            # Wait for any message from the client (e.g., heartbeat)
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        websocket_manager.disconnect(websocket)
