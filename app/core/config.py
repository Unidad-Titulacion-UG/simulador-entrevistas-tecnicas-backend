from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Simulador de Entrevistas Técnicas de Programación"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "API REST para la simulación de entrevistas técnicas de programación."
    )

    DATABASE_URL: str
    FRONTEND_URL: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
