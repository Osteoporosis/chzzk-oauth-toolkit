from __future__ import annotations

from _bootstrap import bootstrap_repo_root

bootstrap_repo_root()

from chzzk_oauth.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["server"]))
