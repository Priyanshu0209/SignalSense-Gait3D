import os
import json
import base64
from cryptography.fernet import Fernet
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "SignalSense"
    API_PREFIX: str = "/api/v1"
    
    # Auth
    SECRET_KEY: str = "supersecret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "admin"
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(os.path.expanduser('~/.signalsense'), 'data', 'signalsense.db')}"
    
    # Router Settings
    ROUTER_ADAPTER: str = "auto"
    ROUTER_HOST: str = "auto"
    ROUTER_USERNAME: str = "root"
    ROUTER_PASSWORD: str = "admin"
    
    # Collector Settings
    UPDATE_INTERVAL_SECONDS: float = 1.0
    
    # Analytics Settings
    ANALYTICS_ENGINE: str = "sqlalchemy"
    CLEANUP_INTERVAL_HOURS: int = 24
    CLEANUP_BATCH_SIZE: int = 1000
    
    DEBUG: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Setup config encryption key (using a fixed key tied to the system for simplicity/portability in a desktop app, or just a hardcoded one for this prototype)
# In a real enterprise app, you'd use OS keyring (DPAPI/Keychain)
ENCRYPTION_KEY = base64.urlsafe_b64encode(b"SignalSense_Enterprise_Key_32bit")
fernet = Fernet(ENCRYPTION_KEY)

config_dir = os.path.expanduser("~/.signalsense")
enc_config_path = os.path.join(config_dir, "config.enc")

if os.path.exists(enc_config_path):
    try:
        with open(enc_config_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data).decode("utf-8")
        config_data = json.loads(decrypted_data)
        
        # Disable overriding settings from encrypted config on startup to force Setup Wizard
        # if "ROUTER_HOST" in config_data: settings.ROUTER_HOST = config_data["ROUTER_HOST"]
        # if "ROUTER_USERNAME" in config_data: settings.ROUTER_USERNAME = config_data["ROUTER_USERNAME"]
        # if "ROUTER_PASSWORD" in config_data: settings.ROUTER_PASSWORD = config_data["ROUTER_PASSWORD"]
    except Exception as e:
        print(f"Failed to load encrypted config: {e}")
