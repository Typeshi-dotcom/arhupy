"""Claude API client integration for arhupy."""

import json
from urllib import error, request


class ClaudeClient:
    """A small Claude API client built with the Python standard library."""

    API_URL = "https://api.anthropic.com/v1/messages"
    API_VERSION = "2023-06-01"

    def __init__(self, api_key, model="claude-opus-4-5"):
        """Create a Claude client with an API key and model name."""
        self.api_key = api_key
        self.model = model

    def ask(self, prompt):
        """Send a filled prompt string to Claude and return the text response."""
        payload = {
            "model": self.model,
            "max_tokens": 1024,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        }
        data = json.dumps(payload).encode("utf-8")
        headers = {
            "anthropic-version": self.API_VERSION,
            "content-type": "application/json",
            "x-api-key": self.api_key,
        }
        api_request = request.Request(
            self.API_URL,
            data=data,
            headers=headers,
            method="POST",
        )

        try:
            with request.urlopen(api_request, timeout=60) as response:
                response_data = json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            message = self._read_http_error(exc)
            raise Exception(f"Claude API request failed: {message}") from exc
        except error.URLError as exc:
            raise Exception(f"Claude API request failed: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise Exception("Claude API response was not valid JSON.") from exc

        return self._extract_text(response_data)

    def ask_with_template(self, prompt_obj, **kwargs):
        """Fill an arhupy Prompt object, send it to Claude, and return text."""
        filled_prompt = prompt_obj.fill(**kwargs)
        return self.ask(filled_prompt)

    def _extract_text(self, response_data):
        """Extract text content blocks from a Claude Messages API response."""
        content_blocks = response_data.get("content", [])
        text_parts = [
            block.get("text", "")
            for block in content_blocks
            if block.get("type") == "text"
        ]
        text = "".join(text_parts).strip()
        if not text:
            raise Exception("Claude API response did not include text content.")
        return text

    def _read_http_error(self, exc):
        """Read a clear error message from a Claude API HTTPError."""
        body = exc.read().decode("utf-8")
        if not body:
            return str(exc)

        try:
            data = json.loads(body)
        except json.JSONDecodeError:
            return body

        error_data = data.get("error", {})
        return error_data.get("message", body)
