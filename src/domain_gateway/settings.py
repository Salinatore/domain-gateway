from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    coap_server_listen_url: str | None = Field(
        default=None,
        description="IP address or hostname for the CoAP server to bind to",
    )

    mqtt_broker_url: str = Field(
        default="localhost",
        description="MQTT broker connection URL",
    )


settings = Settings()
