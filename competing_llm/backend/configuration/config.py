import os

from pydantic import (
    Field,
    SecretStr,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from competing_llm.backend.configuration.config_settings import BasicSettings


class MockLLMSettings(BaseSettings):
    """
    Mock LLM configuration settings.
    """

    # Response length ranges per LLM ID
    response_lengths: dict[int, tuple[int, int]] = Field(
        default={
            1: (30, 60),
            2: (70, 100),
            3: (50, 80),
            4: (40, 90),
            5: (60, 120),
        },
        description="Response length ranges for each LLM ID",
    )

    # Error simulation probabilities (0.0 to 1.0)
    error_rates: dict[str, float] = Field(
        default={
            "rate_limit": 0.05,
            "timeout": 0.03,
            "service_error": 0.02,
        },
        description="Error simulation probabilities",
    )

    # Delay ranges in seconds
    min_delay: float = Field(0.01, description="Minimum delay between chunks", gt=0)
    max_delay: float = Field(0.1, description="Maximum delay between chunks", gt=0)

    # Default streaming delay
    default_delay: float = Field(
        0.05, description="Default delay between chunks", gt=0, le=1.0
    )

    # Enable/disable error simulation
    enable_error_simulation: bool = Field(
        True, description="Enable error simulation for testing"
    )

    # Batch streaming settings
    max_concurrent_llms: int = Field(
        5, description="Maximum concurrent LLMs in batch requests", ge=1, le=10
    )

    model_config = SettingsConfigDict(
        pyproject_toml_table_header=(
            "config",
            os.environ.get("ENVIRONMENT"),
        ),
        pyproject_toml_default_table_header=("config", "default"),
        extra="ignore",
    )


class Settings(BasicSettings):
    """
    Main settings class combining all configuration sections.
    """

    # Overwrite the config table in pyproject.toml
    model_config = SettingsConfigDict(
        pyproject_toml_table_header=(
            "config",
            os.environ.get("ENVIRONMENT"),
        ),
        pyproject_toml_default_table_header=("config", "default"),
        # Ingore unknown CLI arguments
        cli_ignore_unknown_args=True,
    )

    # Mock LLM settings
    mock_llm: MockLLMSettings = Field(default_factory=MockLLMSettings)

    # API settings
    api_title: str = Field("Competing LLM API", description="API title")
    api_version: str = Field("1.0.0", description="API version")
    api_description: str = Field(
        "API for competing LLM chat application with streaming support",
        description="API description",
    )

    # Server settings
    host: str = Field("0.0.0.0", description="Server host")
    port: int = Field(8000, description="Server port", ge=1, le=65535)
    reload: bool = Field(True, description="Enable auto-reload for development")

    # CORS settings
    cors_origins: list[str] = Field(
        ["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins",
    )

    # Supabase settings
    supabase_url: str = Field(
        "",
        alias="SUPABASE_URL",
        description="Supabase project URL used for authentication",
    )
    supabase_service_role_key: SecretStr = Field(
        default=SecretStr(""),
        alias="SUPABASE_SERVICE_ROLE_KEY",
        description="Supabase service role key for privileged server-side auth",
    )

    # Logging settings
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )

    azure_openai_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="azure_openai_api_key, used only for local development",
    )
    azure_openai_endpoint: SecretStr = Field(
        default=SecretStr(""),
        description="azure_openai_endpoint",
    )
    azure_openai_api_version: str = Field(
        default="2025-04-01-preview", description="azure_openai_api_version"
    )
    openrouter_base_url: SecretStr = Field(
        default=SecretStr("https://openrouter.ai/api/v1"),
        description="openrouter_base_url",
    )
    openrouter_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="openrouter_api_key",
    )


config = Settings()
print(config.model_dump_json(indent=2))
