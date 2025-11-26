from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field, SecretStr

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    qwen_api_base: str = Field(..., env="QWEN_API_BASE")
    qwen_api_key: SecretStr = Field(..., env="QWEN_API_KEY")
    langsmith_api_key: SecretStr = Field(..., env="LANGSMITH_API_KEY")
    langsmith_project: str = Field(..., env="LANGSMITH_PROJECT")
    mcp_server: str = Field(..., env="MCP_SERVER")
    database_url: str = Field(default=f"sqlite:///{BASE_DIR / 'data' / 'onboarding.db'}")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"
        case_sensitive = True

    def masked(self) -> "SettingsMasked":
        return SettingsMasked(
            qwen_api_base=self.qwen_api_base,
            mcp_server=self.mcp_server,
            langsmith_project=self.langsmith_project,
            log_level=self.log_level,
        )


class SettingsMasked(BaseSettings):
    qwen_api_base: str
    mcp_server: str
    langsmith_project: str
    log_level: str


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()  # type: ignore[call-arg]
    return _settings


def get_masked_settings() -> SettingsMasked:
    return get_settings().masked()
