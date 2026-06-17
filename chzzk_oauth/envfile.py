from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: str | os.PathLike[str] = ".env") -> None:
    """
    Load a simple KEY=VALUE .env file into os.environ.

    Existing OS environment variables are not overwritten.
    This intentionally supports only common .env syntax to avoid dependencies.
    """
    env_path = Path(path)

    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("export "):
            line = line[len("export ") :].strip()

        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()

        if not key:
            continue

        value = _strip_quotes(value)

        os.environ.setdefault(key, value)


def _strip_quotes(value: str) -> str:
    if len(value) >= 2:
        if value[0] == value[-1] and value[0] in {"'", '"'}:
            return value[1:-1]
    return value
