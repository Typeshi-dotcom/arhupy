"""Unit tests for arhupy."""

import os
import tempfile
import unittest
from io import BytesIO
from urllib import error
from unittest import mock

from arhupy import (
    ClaudeClient,
    Prompt,
    PromptChain,
    estimate_tokens,
    export_chain,
    export_prompt,
    import_chain,
    import_prompt,
    load,
    save,
)


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

    def test_prompt_to_dict_and_from_dict(self):
        """Prompt objects can round-trip through dictionary data."""
        prompt = Prompt("Hello, {name}.")
        prompt.fill(name="Arhu")

        data = prompt.to_dict()
        restored = Prompt.from_dict(data)

        self.assertEqual(data["template"], "Hello, {name}.")
        self.assertEqual(data["filled_values"], {"name": "Arhu"})
        self.assertEqual(restored.template, "Hello, {name}.")
        self.assertEqual(restored.values, {"name": "Arhu"})
        self.assertEqual(str(restored), "Hello, Arhu.")

    def test_prompt_chain_to_dict_and_from_dict(self):
        """PromptChain objects can round-trip through dictionary data."""
        first = Prompt("System: {message}")
        second = Prompt("User: {message}")
        first.fill(message="Be direct.")
        second.fill(message="Explain imports.")
        chain = PromptChain([first, second])

        data = chain.to_dict()
        restored = PromptChain.from_dict(data)

        self.assertEqual(len(data["prompts"]), 2)
        self.assertEqual(restored.build(), "System: Be direct.\nUser: Explain imports.")

    def test_export_prompt_and_import_prompt(self):
        """Prompt objects can round-trip through a JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "prompt.json")
            prompt = Prompt("Translate to {language}: {text}")
            prompt.fill(language="English", text="Hola")

            export_prompt(prompt, filepath)
            restored = import_prompt(filepath)

            self.assertIsInstance(restored, Prompt)
            self.assertEqual(restored.template, "Translate to {language}: {text}")
            self.assertEqual(restored.values, {"language": "English", "text": "Hola"})
            self.assertEqual(str(restored), "Translate to English: Hola")

    def test_export_prompt_writes_pretty_json(self):
        """export_prompt writes readable JSON with two-space indentation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "prompt.json")
            prompt = Prompt("Hello, {name}.")
            prompt.fill(name="Arhu")

            export_prompt(prompt, filepath)

            with open(filepath, "r", encoding="utf-8") as file:
                contents = file.read()

        self.assertTrue(contents.startswith("{\n"))
        self.assertIn('\n  "filled_values": {', contents)
        self.assertTrue(contents.endswith("\n"))

    def test_export_chain_and_import_chain(self):
        """PromptChain objects can round-trip through a JSON file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "chain.json")
            first = Prompt("System: {instruction}")
            second = Prompt("User: {task}")
            first.fill(instruction="Stay practical.")
            second.fill(task="Create a checklist.")
            chain = PromptChain([first, second])

            export_chain(chain, filepath)
            restored = import_chain(filepath)

            self.assertIsInstance(restored, PromptChain)
            self.assertEqual(restored.build(), "System: Stay practical.\nUser: Create a checklist.")

    def test_import_prompt_raises_clear_exception_for_invalid_json(self):
        """import_prompt raises a clear exception for invalid JSON files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "invalid_prompt.json")
            with open(filepath, "w", encoding="utf-8") as file:
                file.write("{invalid json")

            with self.assertRaises(Exception) as context:
                import_prompt(filepath)

        self.assertIn("not valid JSON", str(context.exception))

    def test_import_chain_raises_clear_exception_for_missing_file(self):
        """import_chain raises a clear exception when the file is missing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = os.path.join(temp_dir, "missing_chain.json")

            with self.assertRaises(Exception) as context:
                import_chain(filepath)

        self.assertIn("Could not read prompt chain file", str(context.exception))


if __name__ == "__main__":
    unittest.main()
