import logging
from app.core.config import settings
from app.adapters.analytics.interface import IAnalyticsStorageEngine

logger = logging.getLogger("signalsense.adapters.analytics.factory")

_engine_instance = None

def get_analytics_engine() -> IAnalyticsStorageEngine:

    global _engine_instance
    if _engine_instance is not None:
        return _engine_instance

    engine_type = settings.ANALYTICS_ENGINE.lower()
    
    if engine_type == "sqlalchemy" or engine_type == "sqlite" or engine_type == "postgres":
        from app.adapters.analytics.sqlalchemy_engine import SQLAlchemyAnalyticsEngine
        logger.info(f"Initializing SQLAlchemyAnalyticsEngine for type: {engine_type}")
        _engine_instance = SQLAlchemyAnalyticsEngine()
    elif engine_type == "duckdb":
        # Placeholder for future implementation
        raise NotImplementedError("DuckDB analytics engine not yet implemented.")
    else:
        logger.warning(f"Unknown analytics engine '{engine_type}', defaulting to SQLAlchemy.")
        from app.adapters.analytics.sqlalchemy_engine import SQLAlchemyAnalyticsEngine
        _engine_instance = SQLAlchemyAnalyticsEngine()

    return _engine_instance
