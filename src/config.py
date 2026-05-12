from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # .env içindeki değişken isimleriyle aynı olmalı
    TELEGRAM_BOT_TOKEN: str
    GEMINI_API_KEY: str
    
    # Uygulama genel ayarları
    APP_NAME: str = "Stock Assistant"
    DEBUG: bool = True

    # .env dosyasını bulması için konfigürasyon
    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    """Ayarları önbelleğe alır, her seferinde .env okumaz."""
    return Settings()

settings = get_settings()