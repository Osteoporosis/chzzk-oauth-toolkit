# chzzk-oauth-toolkit

A minimal Python OAuth toolkit for the CHZZK Open API.

## Features

- Build an authorization URL
- Run a local OAuth callback server
- Exchange an authorization code for access and refresh tokens
- Refresh an access token
- Revoke an access or refresh token
- Load configuration from `.env` or environment variables
- Save token responses to a local JSON file
- Ubuntu-based Dev Container
- uv-based development workflow

Runtime dependencies: none. The package uses only the Python standard library.

## Requirements

- Python 3.11+
- uv recommended

The Dev Container includes uv through a Dev Container Feature.

## Dev Container

Open this repository in a Dev Container-compatible editor.

The container uses an Ubuntu base image and installs uv through a feature. No Dockerfile is required.

After the container is created, this command runs automatically:

```bash
uv sync
```

## Local Setup with uv

```bash
uv sync
```

Run with the Python module:

```bash
uv run python -m chzzk_oauth auth-url
```

Run with the console script:

```bash
uv run chzzk-oauth auth-url
```

## Alternative Setup without uv

```bash
python -m pip install -e .
```

Then:

```bash
python -m chzzk_oauth auth-url
```

or:

```bash
chzzk-oauth auth-url
```

## Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Required values:

```bash
CHZZK_CLIENT_ID="..."
CHZZK_CLIENT_SECRET="..."
CHZZK_REDIRECT_URI="http://localhost:8080/callback"
CHZZK_API_BASE_URL="https://openapi.chzzk.naver.com"
```

The authorization documentation describes token endpoints as paths such as `/auth/v1/token`, so this project keeps the API host configurable through `CHZZK_API_BASE_URL`.

## Usage

### 1. Build an authorization URL

```bash
uv run python -m chzzk_oauth auth-url
```

or:

```bash
uv run chzzk-oauth auth-url
```

or:

```bash
uv run python scripts/request_auth_url.py
```

### 2. Run the local callback server

```bash
uv run python -m chzzk_oauth server
```

or:

```bash
uv run python scripts/run_auth_server.py
```

Open the printed URL in your browser. After the callback receives `code` and `state`, the server validates the state, exchanges the code for tokens, and saves the response to `.chzzk_tokens.json`.

### 3. Exchange an authorization code manually

With CLI arguments:

```bash
uv run python -m chzzk_oauth exchange-code --code "AUTH_CODE" --state "STATE"
```

With environment variables:

```bash
CHZZK_AUTH_CODE="AUTH_CODE" CHZZK_AUTH_STATE="STATE" uv run python -m chzzk_oauth exchange-code
```

or:

```bash
uv run python scripts/exchange_code.py
```

### 4. Refresh an access token

Using the saved refresh token:

```bash
uv run python -m chzzk_oauth refresh
```

Using an environment variable:

```bash
CHZZK_REFRESH_TOKEN="REFRESH_TOKEN" uv run python -m chzzk_oauth refresh
```

or:

```bash
uv run python scripts/refresh_token.py
```

### 5. Revoke a token

Revoke an access token:

```bash
uv run python -m chzzk_oauth revoke --token "TOKEN" --token-type-hint access_token
```

or:

```bash
CHZZK_ACCESS_TOKEN="ACCESS_TOKEN" uv run python -m chzzk_oauth revoke
```

Revoke a refresh token:

```bash
CHZZK_REFRESH_TOKEN="REFRESH_TOKEN" CHZZK_TOKEN_TYPE_HINT="refresh_token" uv run python -m chzzk_oauth revoke
```

or:

```bash
uv run python scripts/revoke_token.py
```

### 6. Show the saved token response

```bash
uv run python -m chzzk_oauth show-token
```

## Value Resolution Priority

Values are resolved in this order:

1. CLI argument
2. Environment variable or `.env`
3. Local token file, when applicable

## Security Notes

- Do not commit `.env`.
- Do not commit `.chzzk_tokens.json`.
- Refresh tokens are one-time use. Always keep the latest refresh token returned by the refresh response.
- Access tokens expire according to the API specification.
- Refresh tokens expire according to the API specification.
