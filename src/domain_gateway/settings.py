import logging

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

DEFAULT_COAP_HOST = None
DEFAULT_COAP_PORT = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mqtt_broker_url: str = Field(default="")
    coap_host: str | None = Field(
        default=DEFAULT_COAP_HOST,
        description="Host to bind the CoAP server. Set to '0.0.0.0' in Docker, 'localhost' on macOS.",
    )
    coap_port: int | None = Field(
        default=DEFAULT_COAP_PORT,
        description="Port to bind the CoAP server",
    )


settings = Settings()
