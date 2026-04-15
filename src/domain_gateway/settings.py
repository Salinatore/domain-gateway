from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings, loaded from environment variables or .env file."""

    coap_server_listen_url: str | None = Field(
        default=None,
        description="IP address or hostname for the CoAP server to bind to",
    )

    mqtt_broker_url: str = Field(
        default="localhost",
        description="MQTT broker connection URL",
    )


settings = Settings()
