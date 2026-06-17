from __future__ import annotations

import os
from dataclasses import dataclass

from .envfile import load_env_file


class ConfigError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Config:
    client_id: str
    client_secret: str
    redirect_uri: str
    api_base_url: str

    auth_host: str = "https://chzzk.naver.com"
    token_file: str = ".chzzk_tokens.json"
    state_file: str = ".chzzk_state"

    server_host: str = "127.0.0.1"
    server_port: int = 8080

    auth_code: str | None = None
    auth_state: str | None = None
    access_token: str | None = None
    refresh_token: str | None = None
    token_type_hint: str = "access_token"

    @classmethod
    def from_env(cls, *, load_dotenv: bool = True) -> "Config":
        if load_dotenv:
            load_env_file(".env")

        return cls(
            client_id=_required_env("CHZZK_CLIENT_ID"),
            client_secret=_required_env("CHZZK_CLIENT_SECRET"),
            redirect_uri=_required_env("CHZZK_REDIRECT_URI"),
            api_base_url=_required_env("CHZZK_API_BASE_URL").rstrip("/"),
            auth_host=os.getenv("CHZZK_AUTH_HOST", "https://chzzk.naver.com").rstrip("/"),
            token_file=os.getenv("CHZZK_TOKEN_FILE", ".chzzk_tokens.json"),
            state_file=os.getenv("CHZZK_STATE_FILE", ".chzzk_state"),
            server_host=os.getenv("CHZZK_SERVER_HOST", "127.0.0.1"),
            server_port=_int_env("CHZZK_SERVER_PORT", 8080),
            auth_code=_optional_env("CHZZK_AUTH_CODE"),
            auth_state=_optional_env("CHZZK_AUTH_STATE"),
            access_token=_optional_env("CHZZK_ACCESS_TOKEN"),
            refresh_token=_optional_env("CHZZK_REFRESH_TOKEN"),
            token_type_hint=os.getenv("CHZZK_TOKEN_TYPE_HINT", "access_token"),
        )


def _required_env(name: str) -> str:
    value = _optional_env(name)

    if value is None:
        raise ConfigError(f"Missing required environment variable: {name}")

    return value


def _optional_env(name: str) -> str | None:
    value = os.getenv(name)

    if value is None:
        return None

    value = value.strip()

    return value or None


def _int_env(name: str, default: int) -> int:
    value = _optional_env(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer: {value}") from exc
