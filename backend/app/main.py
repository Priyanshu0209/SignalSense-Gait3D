from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
from app.core.config import settings
from app.core.logger import logger
from app.adapters.router.manager import RouterManager
import app.adapters.router.manager as router_manager_module
from app.collectors.data_collector import get_background_discovery_service
from app.api.websockets import router as ws_router
from app.api.rest import router as rest_router
from app.api import analytics, playback
from app.api.ingest import router as ingest_router
from app.api.metrics import router as metrics_router
from app.api.dataset import router as dataset_router
from app.api.ai import router as ai_router
from app.api.localization import router as localization_router
from app.api.research import router as research_router
from app.api.operations import router as operations_router
from app.api.gait3d import router as gait3d_router, start_gait3d_background, stop_gait3d_background
import uvicorn
from datetime import datetime, timezone

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        description="Enterprise WiFi Monitoring, RSSI Analytics and Live Visualization Platform",
        version="1.0.0",
    )

    # Set all CORS enabled origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify frontend domain
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include Routers
    app.include_router(ws_router)
    app.include_router(rest_router, prefix=settings.API_PREFIX)
    app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])
    app.include_router(playback.router, prefix="/api/v1/playback", tags=["playback"])
    app.include_router(ingest_router, prefix="/api/v1/ingest", tags=["ingest"])
    app.include_router(dataset_router, prefix="/api/v1/dataset", tags=["dataset"])
    app.include_router(ai_router, prefix="/api/v1/ai", tags=["ai"])
    app.include_router(localization_router, prefix="/api/v1/localization", tags=["localization"])
    app.include_router(research_router, prefix="/api/v1/research", tags=["research"])
    app.include_router(operations_router, prefix="/api/v1/operations", tags=["operations"])
    app.include_router(gait3d_router, prefix="/api/v1/gait3d", tags=["gait3d"])
    app.include_router(metrics_router, prefix="/metrics", tags=["observability"])

    # Mount frontend static files
    
    @app.get("/health")
    async def health_check():
        adapter_name = "None"
        router_status = "disconnected"
        if router_manager_module.router_manager:
            if router_manager_module.router_manager.adapter:
                adapter_class = router_manager_module.router_manager.adapter.__class__.__name__
                class_to_name = {
                    "SSHRouterAdapter": "SSH Adapter",
                    "SNMPRouterAdapter": "SNMP Adapter",
                    "RESTRouterAdapter": "REST Adapter",
                    "PassiveDiscoveryAdapter": "Passive Discovery",
                    "MockRouterAdapter": "Mock Adapter",
                    "VendorRouterAdapter": "Vendor Adapter",
                    "NetgearRouterAdapter": "NETGEAR Adapter",
                    "MediaTekTelnetAdapter": "MediaTek Telnet"
                }
                adapter_name = class_to_name.get(adapter_class, adapter_class)
                
            # Check discovery service state
            discovery_svc = get_background_discovery_service()
            if discovery_svc.state.value == "connected":
                router_status = "connected"
            elif discovery_svc.state.value in ["reconnecting", "degraded"]:
                router_status = "error"
            else:
                router_status = "disconnected"

        return {
            "status": "healthy",
            "backend": "running",
            "database": "connected", # Assuming connected if we reach here
            "websocket": "running",
            "router_status": router_status,
            "adapter": adapter_name,
            "version": app.version,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        frontend_dist = os.path.join(sys._MEIPASS, "frontend", "dist")
    else:
        frontend_dist = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
        
    if os.path.exists(frontend_dist):
        app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")
        
        # Mount public folder assets (3D models, images, etc.)
        frontend_public = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "public")
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            frontend_public = os.path.join(sys._MEIPASS, "frontend", "public")
        if os.path.exists(frontend_public):
            # Mount models directory
            models_dir = os.path.join(frontend_public, "models")
            if os.path.exists(models_dir):
                app.mount("/models", StaticFiles(directory=models_dir), name="models")
            # Mount individual GLB files at root level too
            app.mount("/public", StaticFiles(directory=frontend_public), name="public")
        
        @app.get("/")
        async def root():
            response = FileResponse(os.path.join(frontend_dist, "index.html"))
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
            
        @app.get("/{catchall:path}")
        async def catchall(request: Request, catchall: str):
            if catchall.startswith("api/") or catchall.startswith("metrics") or catchall.startswith("models/") or catchall.startswith("public/"):
                return {"detail": "Not Found"}
            response = FileResponse(os.path.join(frontend_dist, "index.html"))
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
    else:
        @app.get("/")
        async def root():
            return {"message": "Welcome to SignalSense API (Frontend missing)"}



    @app.on_event("startup")
    async def startup_event():
        logger.info(f"Starting up {settings.PROJECT_NAME}...")
        
        # Ensure database directory exists and initialize tables
        import os
        from app.db.session import engine, Base
        import app.models.domain  # This is required to populate Base.metadata
        db_dir = os.path.join(os.path.expanduser('~/.signalsense'), 'data')
        os.makedirs(db_dir, exist_ok=True)
        
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            
        # Initialize RouterManager
        router_manager_module.router_manager = RouterManager(
            adapter_type=settings.ROUTER_ADAPTER,
            host=settings.ROUTER_HOST,
            username=settings.ROUTER_USERNAME,
            password=settings.ROUTER_PASSWORD
        )
        
        # Start Background Discovery Service
        discovery_service = get_background_discovery_service()
        discovery_service.router_manager = router_manager_module.router_manager
        await discovery_service.start()
        
        # Initialize Plugin Manager
        from app.sdk.plugins.manager import get_plugin_manager
        import os
        plugin_manager = get_plugin_manager()
        plugins_dir = os.path.join(os.path.dirname(__file__), "..", "plugins")
        plugin_manager.load_plugins_from_directory(plugins_dir)
        await plugin_manager.start_all()
        
        # Start Analytics Storage Service Background Tasks
        from app.services.analytics_storage import get_analytics_storage_service
        analytics_storage = get_analytics_storage_service()
        await analytics_storage.start_background_tasks()

        # Start AI Inference Engine
        from app.services.ai.inference_engine import get_inference_engine
        await get_inference_engine().start()

        # Start Gait3D High-Frequency Collection & Live Visualization Loop
        await start_gait3d_background()

    @app.on_event("shutdown")
    async def shutdown_event():
        logger.info(f"Shutting down {settings.PROJECT_NAME}...")
        discovery_service = get_background_discovery_service()
        await discovery_service.stop()
        
        from app.sdk.plugins.manager import get_plugin_manager
        plugin_manager = get_plugin_manager()
        await plugin_manager.stop_all()
        
        from app.services.analytics_storage import get_analytics_storage_service
        analytics_storage = get_analytics_storage_service()
        await analytics_storage.stop_background_tasks()

        from app.services.ai.inference_engine import get_inference_engine
        await get_inference_engine().stop()

        # Stop Gait3D loop
        await stop_gait3d_background()

    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
