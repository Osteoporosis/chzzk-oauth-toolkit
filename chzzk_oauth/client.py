from __future__ import annotations

import json
import secrets
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .config import Config


class ChzzkOAuthError(RuntimeError):
    """Raised when a CHZZK OAuth HTTP request fails."""


class ChzzkOAuthClient:
    def __init__(self, config: Config):
        self.config = config

    def build_authorization_url(self, state: str | None = None) -> tuple[str, str]:
        state = state or secrets.token_urlsafe(32)

        query = urllib.parse.urlencode(
            {
                "clientId": self.config.client_id,
                "redirectUri": self.config.redirect_uri,
                "state": state,
            }
        )

        return f"{self.config.auth_host}/account-interlock?{query}", state

    def exchange_code(self, *, code: str, state: str) -> dict[str, Any]:
        return self._post_json(
            "/auth/v1/token",
            {
                "grantType": "authorization_code",
                "clientId": self.config.client_id,
                "clientSecret": self.config.client_secret,
                "code": code,
                "state": state,
            },
        )

    def refresh_access_token(self, *, refresh_token: str) -> dict[str, Any]:
        return self._post_json(
            "/auth/v1/token",
            {
                "grantType": "refresh_token",
                "refreshToken": refresh_token,
                "clientId": self.config.client_id,
                "clientSecret": self.config.client_secret,
            },
        )

    def revoke_token(
        self,
        *,
        token: str,
        token_type_hint: str = "access_token",
    ) -> dict[str, Any]:
        if token_type_hint not in {"access_token", "refresh_token"}:
            raise ValueError("token_type_hint must be 'access_token' or 'refresh_token'")

        return self._post_json(
            "/auth/v1/token/revoke",
            {
                "clientId": self.config.client_id,
                "clientSecret": self.config.client_secret,
                "token": token,
                "tokenTypeHint": token_type_hint,
            },
        )

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self.config.api_base_url}{path}"
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")

        request = urllib.request.Request(
            url=url,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Accept": "application/json",
                "User-Agent": "chzzk-oauth-toolkit/0.1.0",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")

                if not raw:
                    return {}

                try:
                    return json.loads(raw)
                except json.JSONDecodeError:
                    return {"raw": raw}

        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise ChzzkOAuthError(
                f"HTTP {exc.code} while POST {path}: {error_body}"
            ) from exc

        except urllib.error.URLError as exc:
            raise ChzzkOAuthError(f"Network error while POST {path}: {exc}") from exc
