"""Unit tests for arhupy."""

import os
import tempfile
import unittest
from io import BytesIO
from urllib import error
from unittest import mock

from arhupy import ClaudeClient, Prompt, PromptChain, estimate_tokens, load, save


class TestPrompt(unittest.TestCase):
    """Tests for prompt rendering and storage helpers."""

    def test_prompt_fill_works_correctly(self):
        """Prompt.fill replaces placeholders with provided values."""
        prompt = Prompt("You are a {role}. Speak in {language}.")

        result = prompt.fill(role="teacher", language="English")

        self.assertEqual(result, "You are a teacher. Speak in English.")
        self.assertEqual(str(prompt), "You are a teacher. Speak in English.")

    def test_prompt_chain_build_joins_prompts(self):
        """PromptChain.build joins prompts with newlines."""
        first = Prompt("System: {message}")
        second = Prompt("User: {message}")
        first.fill(message="Be concise.")
        second.fill(message="Explain tokens.")
        chain = PromptChain([first, second])

        result = chain.build()

        self.assertEqual(result, "System: Be concise.\nUser: Explain tokens.")

    def test_estimate_tokens_returns_correct_integer(self):
        """estimate_tokens returns len(text) / 4 rounded up."""
        self.assertEqual(estimate_tokens("hello"), 2)
        self.assertEqual(estimate_tokens("12345678"), 2)

    def test_save_and_load_from_library_works(self):
        """save and load persist Prompt templates in the working directory."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                prompt = Prompt("Hello, {name}.")

                save("greeting", prompt)
                loaded = load("greeting")

                self.assertIsInstance(loaded, Prompt)
                self.assertEqual(loaded.template, "Hello, {name}.")
                self.assertEqual(loaded.fill(name="Arhu"), "Hello, Arhu.")
            finally:
                os.chdir(original_cwd)

    def test_claude_client_raises_exception_for_invalid_api_key(self):
        """ClaudeClient raises a clear exception when the API call fails."""
        body = b'{"error": {"message": "invalid api key"}}'
        http_error = error.HTTPError(
            url="https://api.anthropic.com/v1/messages",
            code=401,
            msg="Unauthorized",
            hdrs=None,
            fp=BytesIO(body),
        )
        client = ClaudeClient(api_key="invalid-api-key")

        with mock.patch("arhupy.claude.request.urlopen", side_effect=http_error):
            with self.assertRaises(Exception) as context:
                client.ask("Hello, Claude")

        self.assertIn("invalid api key", str(context.exception))


if __name__ == "__main__":
    unittest.main()
