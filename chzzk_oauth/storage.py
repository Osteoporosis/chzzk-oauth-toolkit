from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any


def save_json_atomic(path: str | os.PathLike[str], payload: dict[str, Any]) -> None:
    target = Path(path)
    temp = target.with_suffix(target.suffix + ".tmp")

    temp.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    os.replace(temp, target)


def load_json(path: str | os.PathLike[str]) -> dict[str, Any]:
    target = Path(path)

    if not target.exists():
        return {}

    return json.loads(target.read_text(encoding="utf-8"))


def save_tokens(path: str | os.PathLike[str], token_response: dict[str, Any]) -> None:
    payload = {
        **token_response,
        "savedAt": int(time.time()),
    }

    save_json_atomic(path, payload)


def load_tokens(path: str | os.PathLike[str]) -> dict[str, Any]:
    return load_json(path)


def get_access_token(path: str | os.PathLike[str]) -> str | None:
    return load_tokens(path).get("accessToken")


def get_refresh_token(path: str | os.PathLike[str]) -> str | None:
    return load_tokens(path).get("refreshToken")


def save_state(path: str | os.PathLike[str], state: str) -> None:
    save_json_atomic(
        path,
        {
            "state": state,
            "savedAt": int(time.time()),
        },
    )


def load_state(path: str | os.PathLike[str]) -> str | None:
    return load_json(path).get("state")


def require_value(value: str | None, message: str) -> str:
    if not value:
        raise RuntimeError(message)

    return value
