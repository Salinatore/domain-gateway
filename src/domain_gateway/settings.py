from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""

    mqtt_broker_url: str = Field(
        default="localhost",
        description="MQTT broker connection URL",
    )


settings = Settings()
