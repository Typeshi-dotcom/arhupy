"""Local HTTP API for arhupy."""

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from .diff import compare_prompts
from .improver import improve_prompt
from .scorer import score_prompt


def run_api_server(host="localhost", port=8001):
    """Start the local arhupy API server."""
    server = ThreadingHTTPServer((host, port), APIHandler)
    print(f"API server running at http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("API server stopped.")
    finally:
        server.server_close()


def handle_api_request(path, data):
    """Handle a parsed API request and return a status code and response body."""
    if not isinstance(data, dict):
        return 400, {"error": "Request body must be a JSON object."}

    try:
        if path == "/score":
            return _handle_score(data)
        if path == "/diff":
            return _handle_diff(data)
        if path == "/improve":
            return _handle_improve(data)
    except Exception as exc:
        return 400, {"error": str(exc)}

    return 404, {"error": "Endpoint not found."}


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the local arhupy API."""

    def do_POST(self):
        """Handle POST API requests."""
        try:
            data = self._read_json_body()
        except Exception as exc:
            self._send_json(400, {"error": str(exc)})
            return

        status, response = handle_api_request(self.path, data)
        self._send_json(status, response)

    def do_GET(self):
        """Reject GET requests with a JSON error."""
        self._send_json(405, {"error": "Only POST requests are supported."})

    def log_message(self, format, *args):
        """Silence default request logging to keep CLI output clean."""
        return

    def _read_json_body(self):
        """Read and parse the request JSON body."""
        length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(length)
        if not raw_body:
            raise Exception("Request body is required.")
        try:
            return json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError as exc:
            raise Exception("Request body must be valid JSON.") from exc

    def _send_json(self, status, data):
        """Send a JSON response."""
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _handle_score(data):
    """Handle the /score endpoint."""
    prompt = _require_string(data, "prompt")
    return 200, score_prompt(prompt)


def _handle_diff(data):
    """Handle the /diff endpoint."""
    prompt_1 = _require_string(data, "p1")
    prompt_2 = _require_string(data, "p2")
    return 200, compare_prompts(prompt_1, prompt_2)


def _handle_improve(data):
    """Handle the /improve endpoint."""
    prompt = _require_string(data, "prompt")
    api_key = _require_string(data, "api_key")
    return 200, {"improved_prompt": improve_prompt(prompt, api_key)}


def _require_string(data, key):
    """Return a required string field from request data."""
    value = data.get(key)
    if not isinstance(value, str):
        raise Exception(f"Missing or invalid field: {key}")
    return value
