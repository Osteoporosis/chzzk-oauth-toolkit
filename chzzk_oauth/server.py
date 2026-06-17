from __future__ import annotations

import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .client import ChzzkOAuthClient
from .config import Config
from .storage import save_tokens


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    expected_state: str
    client: ChzzkOAuthClient
    token_file: str
    shutdown_after_success: bool = True

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        expected_path = urlparse(self.client.config.redirect_uri).path or "/"

        if parsed.path != expected_path:
            self._send_html(404, "<h1>404 Not Found</h1>")
            return

        params = parse_qs(parsed.query)
        code = _first(params, "code")
        state = _first(params, "state")

        if not code or not state:
            self._send_html(400, "<h1>Missing code or state</h1>")
            return

        if state != self.expected_state:
            self._send_html(400, "<h1>Invalid state</h1>")
            return

        try:
            tokens = self.client.exchange_code(code=code, state=state)
            save_tokens(self.token_file, tokens)
        except Exception as exc:
            self._send_html(
                500,
                f"<h1>Token exchange failed</h1><pre>{html.escape(str(exc))}</pre>",
            )
            return

        self._send_html(
            200,
            """
            <h1>CHZZK OAuth success</h1>
            <p>Token response saved. You may close this window.</p>
            """,
        )

        if self.shutdown_after_success:
            self.server.shutdown()

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send_html(self, status: int, body: str) -> None:
        content = f"<!doctype html><html><body>{body}</body></html>".encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)


def run_callback_server(config: Config) -> None:
    client = ChzzkOAuthClient(config)
    authorization_url, state = client.build_authorization_url()

    OAuthCallbackHandler.expected_state = state
    OAuthCallbackHandler.client = client
    OAuthCallbackHandler.token_file = config.token_file

    server = ThreadingHTTPServer(
        (config.server_host, config.server_port),
        OAuthCallbackHandler,
    )

    print("Open this URL in your browser:")
    print(authorization_url)
    print()
    print(f"Listening on http://{config.server_host}:{config.server_port}")
    print(f"Token file: {config.token_file}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


def _first(params: dict[str, list[str]], key: str) -> str | None:
    values = params.get(key)
    return values[0] if values else None
