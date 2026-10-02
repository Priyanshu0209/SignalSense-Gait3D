import asyncio
import logging
import json
from typing import List, Dict, Set
from fastapi import WebSocket
from fastapi.encoders import jsonable_encoder

logger = logging.getLogger("signalsense.websockets")

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast_event(self, event_name: str, payload: dict | list):
        if not self.active_connections:
            return
        
        # Module 8: Frontend Validation - validate payloads before broadcasting to React
        if event_name == "device_updated" and isinstance(payload, list):
            try:
                from app.services.diagnostics.frontend_validation import get_frontend_validation_service
                from datetime import datetime, timezone
                fe_verifier = get_frontend_validation_service()
                if not fe_verifier._running:
                    await fe_verifier.start()
                    
                # React expects these properties per the ConnectedDevice interface
                react_required_props = {
                    "mac": ("RSSI Chart", "str"),
                    "rssi": ("RSSI Chart", "int"),
                    "signal": ("Signal History", "str"),
                    "hostname": ("Device Card", "str"),
                    "status": ("Status Badge", "str"),
                    "connection_duration": ("Timeline", "int"),
                    "trend": ("Trend Chart", "str"),
                    "timestamp": ("Timeline", "str"),
                    "distance": ("Device Card", "str"),
                    "animation": ("Animation", "dict")
                }
                
                for dev_payload in payload:
                    if not isinstance(dev_payload, dict):
                        continue
                    mac = dev_payload.get("mac", "Unknown")
                    
                    for prop, (component, expected) in react_required_props.items():
                        actual = dev_payload.get(prop)
                        
                        if actual is None:
                            val_result = "NULL"
                            severity = "HIGH" if prop in ("rssi", "mac") else "MEDIUM"
                        elif actual == "Unknown" or actual == "" or actual == "None":
                            val_result = "MISSING_PROPERTY"
                            severity = "MEDIUM"
                        elif prop == "rssi" and not isinstance(actual, (int, float)):
                            val_result = "CHART_ERROR"
                            severity = "HIGH"
                        elif prop == "connection_duration" and not isinstance(actual, (int, float)):
                            val_result = "TIMELINE_ERROR"
                            severity = "MEDIUM"
                        else:
                            val_result = "PASS"
                            severity = "INFO"
                            
                        if val_result != "PASS":
                            fe_verifier.log_validation({
                                "Timestamp": datetime.now(timezone.utc).isoformat(),
                                "Component": component,
                                "Discovery Scan ID": "N/A",
                                "Correlation ID": "N/A",
                                "MAC Address": mac,
                                "Property": prop,
                                "Expected": expected,
                                "Actual": str(actual),
                                "Validation Result": val_result,
                                "Severity": severity,
                                "Render Time": 0.0,
                                "Thread": "WebSocket"
                            })
            except Exception as fe_err:
                logger.warning(f"Frontend validation error: {fe_err}")
            
        message = json.dumps(jsonable_encoder({"event": event_name, "data": payload}))
        
        # Broadcast concurrently
        tasks = []
        for connection in list(self.active_connections):
            tasks.append(self._send_message(connection, message))
            
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_message(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.warning(f"Failed to send websocket message, disconnecting client. Error: {e}")
            self.disconnect(websocket)

# Singleton manager
websocket_manager = ConnectionManager()
