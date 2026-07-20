"""Environment-driven application settings."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    product_name: str = Field(
        default="Nha Trang Trip Planner Agent",
        validation_alias="PRODUCT_NAME",
    )

    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o-mini", validation_alias="LLM_MODEL")
    embedding_model: str = Field(
        default="text-embedding-3-small",
        validation_alias="EMBEDDING_MODEL",
    )
    temperature: float = Field(default=0.0, validation_alias="TEMPERATURE")

    k_results: int = Field(default=4, validation_alias="K_RESULTS")
    faiss_index_path: str = Field(
        default="faiss_index_openai_embeddings",
        validation_alias="SAVE_PATH",
    )

    serpapi_api_key: str = Field(default="", validation_alias="SERPAPI_API_KEY")
    default_location: str = Field(
        default="Nha Trang, Việt Nam",
        validation_alias="DEFAULT_LOCATION",
    )
    food_max_results: int = Field(default=5, validation_alias="FOOD_MAX_RESULTS")
    search_language: str = Field(default="vi", validation_alias="SEARCH_LANGUAGE")
    search_country: str = Field(default="vn", validation_alias="SEARCH_COUNTRY")
    google_domain: str = Field(default="google.com.vn", validation_alias="GOOGLE_DOMAIN")

    langfuse_public_key: str = Field(default="", validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: str = Field(default="", validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(
        default="http://localhost:3000",
        validation_alias="LANGFUSE_HOST",
    )

    max_message_chars: int = Field(default=8000, validation_alias="MAX_MESSAGE_CHARS")
    enable_openai_moderation: bool = Field(
        default=False,
        validation_alias="ENABLE_OPENAI_MODERATION",
    )

    cors_origins: str = Field(default="*", validation_alias="CORS_ORIGINS")
    api_prefix: str = Field(default="/api/v1", validation_alias="API_PREFIX")


@lru_cache
def get_settings() -> Settings:
    return Settings()
