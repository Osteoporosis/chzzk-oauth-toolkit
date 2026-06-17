from __future__ import annotations

import argparse
import json
import sys

from .client import ChzzkOAuthClient
from .config import Config, ConfigError
from .server import run_callback_server
from .storage import (
    get_access_token,
    get_refresh_token,
    load_state,
    load_tokens,
    require_value,
    save_state,
    save_tokens,
)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        config = Config.from_env()
        client = ChzzkOAuthClient(config)

        if args.command == "auth-url":
            return command_auth_url(args, config, client)

        if args.command == "server":
            run_callback_server(config)
            return 0

        if args.command == "exchange-code":
            return command_exchange_code(args, config, client)

        if args.command == "refresh":
            return command_refresh(config, client)

        if args.command == "revoke":
            return command_revoke(args, config, client)

        if args.command == "show-token":
            return command_show_token(config)

        parser.print_help()
        return 1

    except (ConfigError, RuntimeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="chzzk-oauth",
        description="Minimal CHZZK OAuth helper",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    auth_url = subparsers.add_parser("auth-url", help="Print authorization URL")
    auth_url.add_argument(
        "--state",
        help="Optional state. If omitted, a secure random state is generated.",
    )
    auth_url.add_argument(
        "--save-state",
        action="store_true",
        help="Save generated state to CHZZK_STATE_FILE.",
    )

    subparsers.add_parser("server", help="Run local callback server")

    exchange = subparsers.add_parser(
        "exchange-code",
        help="Exchange authorization code for tokens",
    )
    exchange.add_argument("--code", help="Authorization code")
    exchange.add_argument("--state", help="Authorization state")

    subparsers.add_parser(
        "refresh",
        help="Refresh access token using refresh token",
    )

    revoke = subparsers.add_parser("revoke", help="Revoke access or refresh token")
    revoke.add_argument("--token", help="Token to revoke")
    revoke.add_argument(
        "--token-type-hint",
        choices=["access_token", "refresh_token"],
        help="Token type hint",
    )

    subparsers.add_parser(
        "show-token",
        help="Show locally saved token response",
    )

    return parser


def command_auth_url(
    args: argparse.Namespace,
    config: Config,
    client: ChzzkOAuthClient,
) -> int:
    authorization_url, state = client.build_authorization_url(state=args.state)

    if args.save_state:
        save_state(config.state_file, state)

    print(
        json.dumps(
            {
                "authorizationUrl": authorization_url,
                "state": state,
                "stateSaved": bool(args.save_state),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


def command_exchange_code(
    args: argparse.Namespace,
    config: Config,
    client: ChzzkOAuthClient,
) -> int:
    code = first_present(args.code, config.auth_code)
    state = first_present(args.state, config.auth_state, load_state(config.state_file))

    code = require_value(
        code,
        "Missing authorization code. Use --code or CHZZK_AUTH_CODE.",
    )
    state = require_value(
        state,
        "Missing state. Use --state, CHZZK_AUTH_STATE, or saved state file.",
    )

    tokens = client.exchange_code(code=code, state=state)
    save_tokens(config.token_file, tokens)

    print(json.dumps(tokens, ensure_ascii=False, indent=2))
    print(f"Saved token response to {config.token_file}", file=sys.stderr)

    return 0


def command_refresh(config: Config, client: ChzzkOAuthClient) -> int:
    refresh_token = first_present(
        config.refresh_token,
        get_refresh_token(config.token_file),
    )

    refresh_token = require_value(
        refresh_token,
        "Missing refresh token. Use CHZZK_REFRESH_TOKEN or saved token file.",
    )

    tokens = client.refresh_access_token(refresh_token=refresh_token)
    save_tokens(config.token_file, tokens)

    print(json.dumps(tokens, ensure_ascii=False, indent=2))
    print(f"Saved refreshed token response to {config.token_file}", file=sys.stderr)

    return 0


def command_revoke(
    args: argparse.Namespace,
    config: Config,
    client: ChzzkOAuthClient,
) -> int:
    token_type_hint = first_present(
        args.token_type_hint,
        config.token_type_hint,
    )

    token: str | None

    if args.token:
        token = args.token
    elif token_type_hint == "refresh_token":
        token = first_present(config.refresh_token, get_refresh_token(config.token_file))
    else:
        token = first_present(config.access_token, get_access_token(config.token_file))

    token = require_value(
        token,
        "Missing token. Use --token, CHZZK_ACCESS_TOKEN, CHZZK_REFRESH_TOKEN, or saved token file.",
    )

    response = client.revoke_token(
        token=token,
        token_type_hint=token_type_hint,
    )

    print(json.dumps(response, ensure_ascii=False, indent=2))

    return 0


def command_show_token(config: Config) -> int:
    tokens = load_tokens(config.token_file)

    if not tokens:
        print(f"No token file found: {config.token_file}", file=sys.stderr)
        return 1

    print(json.dumps(tokens, ensure_ascii=False, indent=2))
    return 0


def first_present(*values: str | None) -> str | None:
    for value in values:
        if value:
            return value
    return None


if __name__ == "__main__":
    raise SystemExit(main())
