"""Unit tests for arhupy."""

import json
import os
import tempfile
import unittest
from io import BytesIO, StringIO
from urllib import error
from unittest import mock

from arhupy import (
    ClaudeClient,
    Prompt,
    PromptChain,
    add_history,
    build_chain,
    compare_history,
    compare_prompts,
    estimate_tokens,
    export_all,
    export_chain,
    export_history,
    export_prompt,
    fill_template,
    get_template,
    get_history,
    get_plugin,
    get_prompt_by_index,
    improve_prompt,
    import_all,
    import_chain,
    import_history,
    import_prompt,
    list_all,
    list_templates,
    load_plugins,
    load,
    run_interactive,
    save,
    save_version,
    score_prompt,
)
from arhupy.api import handle_api_request
from arhupy.cli import main as cli_main
from arhupy.web import render_comparison, render_page, render_save_result, render_score


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

    def test_build_chain_with_two_prompts(self):
        """build_chain joins two prompt strings with a newline."""
        result = build_chain(["System: Be concise.", "User: Explain tokens."])

        self.assertEqual(result, "System: Be concise.\nUser: Explain tokens.")

    def test_build_chain_with_multiple_prompts(self):
        """build_chain joins multiple prompt strings in order."""
        result = build_chain(["One", "Two", "Three"])

        self.assertEqual(result, "One\nTwo\nThree")

    def test_build_chain_empty_input(self):
        """build_chain returns an empty string for no prompts."""
        self.assertEqual(build_chain([]), "")

    def test_estimate_tokens_returns_correct_integer(self):
        """estimate_tokens returns len(text) / 4 rounded up."""
        self.assertEqual(estimate_tokens("hello"), 2)
        self.assertEqual(estimate_tokens("12345678"), 2)

    def test_api_score_returns_json_ready_response(self):
        """The API score handler returns score data as JSON-ready output."""
        status, response = handle_api_request("/score", {"prompt": "You are a coach"})
        encoded = json.dumps(response)

        self.assertEqual(status, 200)
        self.assertIn("overall_score", response)
        self.assertIsInstance(encoded, str)

    def test_api_diff_returns_json_ready_response(self):
        """The API diff handler returns comparison data as JSON-ready output."""
        status, response = handle_api_request("/diff", {"p1": "a b", "p2": "a c"})
        encoded = json.dumps(response)

        self.assertEqual(status, 200)
        self.assertEqual(response["common_words"], ["a"])
        self.assertIsInstance(encoded, str)

    def test_api_improve_returns_json_response(self):
        """The API improve handler returns improved prompt JSON."""
        with mock.patch("arhupy.api.improve_prompt", return_value="Improved prompt"):
            status, response = handle_api_request(
                "/improve",
                {"prompt": "You are a coach", "api_key": "test-key"},
            )
        encoded = json.dumps(response)

        self.assertEqual(status, 200)
        self.assertEqual(response["improved_prompt"], "Improved prompt")
        self.assertIsInstance(encoded, str)

    def test_api_bad_request_returns_json_error(self):
        """The API handler returns clean JSON errors for bad requests."""
        status, response = handle_api_request("/score", {})
        encoded = json.dumps(response)

        self.assertEqual(status, 400)
        self.assertIn("error", response)
        self.assertIsInstance(encoded, str)

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

    def test_export_all_and_import_all_merge_without_overwriting(self):
        """export_all and import_all share libraries without overwriting conflicts."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                save("existing", Prompt("Keep this."))
                export_path = os.path.join(temp_dir, "prompts.json")
                with open(export_path, "w", encoding="utf-8") as file:
                    json.dump(
                        {
                            "existing": "Do not overwrite.",
                            "new_prompt": "You are a coach.",
                        },
                        file,
                    )

                result = import_all(export_path)
                second_export = os.path.join(temp_dir, "second_export.json")
                export_all(second_export)

                self.assertEqual(result["imported"], ["new_prompt"])
                self.assertEqual(result["skipped"], ["existing"])
                self.assertEqual(load("existing").template, "Keep this.")
                self.assertEqual(load("new_prompt").template, "You are a coach.")
                with open(second_export, "r", encoding="utf-8") as file:
                    exported = json.load(file)
                self.assertEqual(exported["existing"], "Keep this.")
                self.assertEqual(exported["new_prompt"], "You are a coach.")
            finally:
                os.chdir(original_cwd)

    def test_list_all_prints_count_and_prompt_names(self):
        """list_all prints a count and formatted prompt names."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                save("alpha", Prompt("Prompt A"))

                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    list_all()

                contents = output.getvalue()
                self.assertIn("Saved prompts: 1 prompt", contents)
                self.assertIn("- alpha", contents)
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

    def test_improve_prompt_uses_claude_client(self):
        """improve_prompt sends an improvement request through ClaudeClient."""
        with mock.patch("arhupy.improver.ClaudeClient") as client_class:
            client = client_class.return_value
            client.ask.return_value = "You are a supportive fitness coach."

            result = improve_prompt("You are a coach", "test-key")

        self.assertEqual(result, "You are a supportive fitness coach.")
        client_class.assert_called_once_with(api_key="test-key")
        request_text = client.ask.call_args.args[0]
        self.assertIn("Improve this prompt", request_text)
        self.assertIn("You are a coach", request_text)

    def test_improve_prompt_requires_api_key_and_prompt_text(self):
        """improve_prompt raises clear errors for missing required inputs."""
        with self.assertRaises(Exception) as missing_context:
            improve_prompt("You are a coach", "")
        with self.assertRaises(Exception) as empty_prompt_context:
            improve_prompt("", "test-key")

        self.assertIn("API key is required", str(missing_context.exception))
        self.assertIn("Prompt text is required", str(empty_prompt_context.exception))

    def test_improve_prompt_supports_placeholder_demo_key(self):
        """improve_prompt returns a local demo improvement for placeholder keys."""
        result = improve_prompt("You are a coach", "YOUR_KEY")

        self.assertIn("You are a coach", result)
        self.assertIn("clear", result.lower())
        self.assertIn("structured", result.lower())

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

    def test_score_prompt_returns_scores_and_feedback(self):
        """score_prompt returns numeric scores and feedback suggestions."""
        result = score_prompt("You are a {role}. Explain this: {question}")

        self.assertEqual(set(result), {
            "length_score",
            "clarity_score",
            "structure_score",
            "overall_score",
            "feedback",
            "strengths",
        })
        self.assertIsInstance(result["overall_score"], int)
        self.assertGreaterEqual(result["overall_score"], 0)
        self.assertLessEqual(result["overall_score"], 10)
        self.assertIsInstance(result["feedback"], list)
        self.assertIsInstance(result["strengths"], list)

    def test_score_prompt_short_prompt_gets_low_score(self):
        """score_prompt gives short prompts a low score and useful feedback."""
        result = score_prompt("hi")

        self.assertLessEqual(result["overall_score"], 3)
        self.assertIn("Add more detail", result["feedback"][0])

    def test_score_prompt_strong_prompt_gets_high_score(self):
        """score_prompt rewards prompts with role, task, structure, and constraints."""
        result = score_prompt(
            "You are a {role}. Explain {task} step by step in bullet points within 200 words only."
        )

        self.assertGreaterEqual(result["overall_score"], 9)
        self.assertIn("Role is defined", result["strengths"])
        self.assertIn("Clear task defined", result["strengths"])
        self.assertIn("Good structure", result["strengths"])

    def test_score_prompt_strong_natural_prompt_gets_high_score(self):
        """score_prompt rewards clear natural-language prompts."""
        result = score_prompt(
            "You are a fitness coach. Explain progressive overload step by step."
        )

        self.assertGreaterEqual(result["overall_score"], 8)
        self.assertIn("Good prompt length", result["strengths"])
        self.assertIn("Role is defined", result["strengths"])
        self.assertIn("Clear task defined", result["strengths"])

    def test_score_prompt_empty_prompt_is_handled(self):
        """score_prompt handles empty prompts without crashing."""
        result = score_prompt("")

        self.assertEqual(result["overall_score"], 0)
        self.assertIn("Add prompt text before scoring.", result["feedback"])
        self.assertIn("Ready for improvement", result["strengths"])

    def test_template_exists(self):
        """Built-in templates can be listed and loaded by name."""
        templates = list_templates()
        template = get_template("coding")

        self.assertIn("coding", templates)
        self.assertEqual(
            template,
            "You are a senior developer. Explain {concept} in simple terms.",
        )

    def test_invalid_template_name_raises_clear_error(self):
        """Loading an unknown template raises a clear exception."""
        with self.assertRaises(Exception) as context:
            get_template("unknown")

        self.assertIn("Template not found", str(context.exception))

    def test_fill_template_replaces_placeholder(self):
        """fill_template asks for placeholder values and returns a filled prompt."""
        with mock.patch("builtins.input", return_value="recursion"):
            result = fill_template("coding")

        self.assertEqual(
            result,
            "You are a senior developer. Explain recursion in simple terms.",
        )

    def test_fill_template_replaces_multiple_placeholders(self):
        """fill_template replaces every placeholder in a template."""
        values = iter(["weekly workout plan", "building strength"])
        with mock.patch("builtins.input", side_effect=lambda _: next(values)):
            result = fill_template("fitness")

        self.assertEqual(
            result,
            "You are a fitness coach. Create a weekly workout plan for building strength.",
        )

    def test_fill_template_missing_template_raises_clear_error(self):
        """fill_template reports missing template names clearly."""
        with self.assertRaises(Exception) as context:
            fill_template("unknown")

        self.assertIn("Template not found", str(context.exception))

    def test_cli_templates_commands_print_templates(self):
        """The templates CLI commands list and print built-in templates."""
        with mock.patch("sys.stdout", new_callable=StringIO) as list_output:
            list_exit_code = cli_main(["templates"])
        with mock.patch("sys.stdout", new_callable=StringIO) as template_output:
            template_exit_code = cli_main(["template", "coding"])

        self.assertEqual(list_exit_code, 0)
        self.assertEqual(template_exit_code, 0)
        self.assertIn("Available templates:", list_output.getvalue())
        self.assertIn("- coding", list_output.getvalue())
        self.assertIn("You are a senior developer", template_output.getvalue())

    def test_cli_template_handles_invalid_name(self):
        """The template CLI command reports invalid names cleanly."""
        with mock.patch("sys.stdout", new_callable=StringIO) as output:
            exit_code = cli_main(["template", "unknown"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: Template not found", output.getvalue())

    def test_cli_fill_prints_filled_template(self):
        """The fill CLI command fills and prints a built-in template."""
        with mock.patch("builtins.input", return_value="recursion"):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["fill", "coding"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Explain recursion", output.getvalue())

    def test_cli_fill_handles_missing_template(self):
        """The fill CLI command reports missing template names cleanly."""
        with mock.patch("sys.stdout", new_callable=StringIO) as output:
            exit_code = cli_main(["fill", "unknown"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: Template not found", output.getvalue())

    def test_cli_chain_builds_prompt_chain(self):
        """The chain CLI command collects prompts and prints a combined chain."""
        inputs = iter(["Prompt one", "Prompt two", ""])
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["chain"])

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Final prompt chain:", contents)
        self.assertIn("Prompt one\nPrompt two", contents)

    def test_cli_chain_handles_empty_input(self):
        """The chain CLI command handles empty input cleanly."""
        with mock.patch("builtins.input", return_value=""):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["chain"])

        self.assertEqual(exit_code, 0)
        self.assertIn("No prompts entered.", output.getvalue())

    def test_history_save(self):
        """Prompt history saves prompts with timestamps."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                entry = add_history("You are a coach.")
                history = get_history()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(entry["prompt"], "You are a coach.")
        self.assertIn("timestamp", entry)
        self.assertEqual(history[0]["prompt"], "You are a coach.")

    def test_history_limit(self):
        """Prompt history can return a limited number of latest entries."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                add_history("First prompt")
                add_history("Second prompt")
                limited = get_history(limit=1)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(len(limited), 1)
        self.assertEqual(limited[0]["prompt"], "Second prompt")

    def test_history_reuse_by_index(self):
        """Prompt history can reuse prompts by one-based latest-first index."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                add_history("First prompt")
                add_history("Second prompt")
                latest = get_prompt_by_index(1)
                older = get_prompt_by_index(2)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(latest, "Second prompt")
        self.assertEqual(older, "First prompt")

    def test_history_invalid_index_raises_clear_error(self):
        """Prompt history raises a clear error for invalid indexes."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                add_history("Only prompt")
                with self.assertRaises(Exception) as context:
                    get_prompt_by_index(2)
            finally:
                os.chdir(original_cwd)

        self.assertIn("No prompt found", str(context.exception))

    def test_compare_history_valid_indexes(self):
        """compare_history compares two prompts by history index."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                add_history("You are a coach")
                add_history("You are a strict fitness coach")
                result = compare_history(1, 2)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(result["prompt_1"], "You are a strict fitness coach")
        self.assertEqual(result["prompt_2"], "You are a coach")
        self.assertIn("length_diff", result["comparison"])
        self.assertIn("common_words", result["comparison"])

    def test_compare_history_invalid_index_raises_clear_error(self):
        """compare_history reports invalid history indexes clearly."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                add_history("Only prompt")
                with self.assertRaises(Exception) as context:
                    compare_history(1, 2)
            finally:
                os.chdir(original_cwd)

        self.assertIn("No prompt found", str(context.exception))

    def test_compare_history_same_index(self):
        """compare_history supports comparing a prompt with itself."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                add_history("Same prompt")
                result = compare_history(1, 1)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(result["prompt_1"], "Same prompt")
        self.assertEqual(result["prompt_2"], "Same prompt")
        self.assertEqual(result["comparison"]["length_diff"], 0)
        self.assertEqual(result["comparison"]["word_diff"], 0)

    def test_export_history_file(self):
        """export_history writes full history to a JSON file."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                filepath = os.path.join(temp_dir, "history_export.json")

                add_history("Export me")
                export_history(filepath)
                with open(filepath, "r", encoding="utf-8") as file:
                    data = json.load(file)
            finally:
                os.chdir(original_cwd)

        self.assertEqual(data[0]["prompt"], "Export me")
        self.assertIn("timestamp", data[0])

    def test_import_history(self):
        """import_history loads entries into local history."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                filepath = os.path.join(temp_dir, "history_import.json")
                with open(filepath, "w", encoding="utf-8") as file:
                    json.dump([
                        {"prompt": "Imported prompt", "timestamp": "2026-01-01T00:00:00+00:00"}
                    ], file)

                result = import_history(filepath)
                history = get_history()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(len(result["imported"]), 1)
        self.assertEqual(history[0]["prompt"], "Imported prompt")

    def test_import_history_skips_duplicates(self):
        """import_history does not duplicate existing entries."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                filepath = os.path.join(temp_dir, "history_import.json")
                data = [
                    {"prompt": "Imported prompt", "timestamp": "2026-01-01T00:00:00+00:00"}
                ]
                with open(filepath, "w", encoding="utf-8") as file:
                    json.dump(data, file)

                first = import_history(filepath)
                second = import_history(filepath)
                history = get_history()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(len(first["imported"]), 1)
        self.assertEqual(len(second["imported"]), 0)
        self.assertEqual(second["skipped"], 1)
        self.assertEqual(len(history), 1)

    def test_get_history_keeps_version_history_compatibility(self):
        """get_history still supports version history lookups by prompt name."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                prompt = Prompt("Hello, {name}.")
                save_version("greeting", prompt, "1.0.0", notes="Initial")
                versions = get_history("greeting")
                versions_by_name = get_history(name="greeting")
            finally:
                os.chdir(original_cwd)

        self.assertEqual(versions[0]["version"], "1.0.0")
        self.assertEqual(versions_by_name[0]["notes"], "Initial")

    def test_cli_history_and_reuse_commands(self):
        """History and reuse CLI commands show recent prompts."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                add_history("First prompt")
                add_history("Second prompt")

                with mock.patch("sys.stdout", new_callable=StringIO) as history_output:
                    history_exit_code = cli_main(["history", "1"])
                with mock.patch("sys.stdout", new_callable=StringIO) as reuse_output:
                    reuse_exit_code = cli_main(["reuse", "2"])
            finally:
                os.chdir(original_cwd)

        self.assertEqual(history_exit_code, 0)
        self.assertEqual(reuse_exit_code, 0)
        self.assertIn("Recent prompts:", history_output.getvalue())
        self.assertIn("Second prompt", history_output.getvalue())
        self.assertNotIn("First prompt", history_output.getvalue())
        self.assertIn("First prompt", reuse_output.getvalue())

    def test_cli_compare_history_prints_comparison(self):
        """The compare-history CLI command compares saved history prompts."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                add_history("You are a coach")
                add_history("You are a strict fitness coach")

                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    exit_code = cli_main(["compare-history", "1", "2"])
            finally:
                os.chdir(original_cwd)

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Prompt 1:", contents)
        self.assertIn("Prompt 2:", contents)
        self.assertIn("Score comparison:", contents)
        self.assertIn("Better prompt:", contents)

    def test_cli_compare_history_handles_invalid_index(self):
        """The compare-history CLI command reports invalid indexes cleanly."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                add_history("Only prompt")

                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    exit_code = cli_main(["compare-history", "1", "2"])
            finally:
                os.chdir(original_cwd)

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: No prompt found", output.getvalue())

    def test_cli_export_and_import_history(self):
        """CLI export-history and import-history share prompt history."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                filepath = os.path.join(temp_dir, "history.json")
                add_history("CLI export prompt")

                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    export_exit_code = cli_main(["export-history", filepath])
                    import_exit_code = cli_main(["import-history", filepath])
            finally:
                os.chdir(original_cwd)

        contents = output.getvalue()
        self.assertEqual(export_exit_code, 0)
        self.assertEqual(import_exit_code, 0)
        self.assertIn("Exported history to", contents)
        self.assertIn("Skipped duplicates: 1", contents)

    def test_cli_reuse_handles_invalid_index(self):
        """The reuse CLI command reports invalid indexes cleanly."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    exit_code = cli_main(["reuse", "1"])
            finally:
                os.chdir(original_cwd)

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: No prompt found", output.getvalue())

    def test_interactive_score_and_exit(self):
        """Interactive mode can score a prompt and exit."""
        inputs = iter(["You are a coach", "1", "5"])
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                run_interactive()

        contents = output.getvalue()
        self.assertIn("Welcome to arhupy interactive mode.", contents)
        self.assertIn("Score:", contents)
        self.assertIn("Goodbye.", contents)

    def test_interactive_handles_invalid_option(self):
        """Interactive mode reports invalid menu choices cleanly."""
        inputs = iter(["You are a coach", "bad", "5"])
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                run_interactive()

        self.assertIn("Invalid option", output.getvalue())

    def test_interactive_fill_template_and_exit(self):
        """Interactive mode can fill a built-in template and exit."""
        inputs = iter(["You are a coach", "6", "coding", "recursion", "5"])
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                run_interactive()

        contents = output.getvalue()
        self.assertIn("Filled prompt:", contents)
        self.assertIn("Explain recursion", contents)

    def test_interactive_build_chain_and_exit(self):
        """Interactive mode can build a prompt chain and exit."""
        inputs = iter(["You are a coach", "7", "Prompt one", "Prompt two", "", "5"])
        with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                run_interactive()

        contents = output.getvalue()
        self.assertIn("Final prompt chain:", contents)
        self.assertIn("Prompt one\nPrompt two", contents)

    def test_interactive_compare_history_and_exit(self):
        """Interactive mode can compare prompts from history."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                add_history("You are a coach")
                add_history("You are a strict fitness coach")
                inputs = iter(["Starter prompt", "8", "1", "2", "5"])

                with mock.patch("builtins.input", side_effect=lambda _: next(inputs)):
                    with mock.patch("sys.stdout", new_callable=StringIO) as output:
                        run_interactive()
            finally:
                os.chdir(original_cwd)

        contents = output.getvalue()
        self.assertIn("Prompt 1:", contents)
        self.assertIn("Score comparison:", contents)
        self.assertIn("Better prompt:", contents)

    def test_interactive_export_and_import_history(self):
        """Interactive mode can export and import prompt history."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                filepath = os.path.join(temp_dir, "history.json")
                add_history("Interactive export prompt")

                export_inputs = iter(["Starter prompt", "9", filepath, "5"])
                with mock.patch("builtins.input", side_effect=lambda _: next(export_inputs)):
                    with mock.patch("sys.stdout", new_callable=StringIO) as export_output:
                        run_interactive()

                import_inputs = iter(["Starter prompt", "10", filepath, "5"])
                with mock.patch("builtins.input", side_effect=lambda _: next(import_inputs)):
                    with mock.patch("sys.stdout", new_callable=StringIO) as import_output:
                        run_interactive()
            finally:
                os.chdir(original_cwd)

        self.assertIn("Exported history to", export_output.getvalue())
        self.assertIn("Skipped duplicates: 1", import_output.getvalue())

    def test_cli_interactive_calls_run_interactive(self):
        """The interactive CLI command starts interactive mode."""
        with mock.patch("arhupy.cli.run_interactive") as interactive:
            exit_code = cli_main(["interactive"])

        self.assertEqual(exit_code, 0)
        interactive.assert_called_once_with()

    def test_cli_api_calls_run_api_server(self):
        """The api CLI command starts the local API server."""
        with mock.patch("arhupy.cli.run_api_server") as api_server:
            exit_code = cli_main(["api"])

        self.assertEqual(exit_code, 0)
        api_server.assert_called_once_with()

    def test_plugin_load(self):
        """load_plugins discovers bundled plugins."""
        plugins = load_plugins()

        self.assertIn("echo", plugins)

    def test_plugin_execution(self):
        """The echo plugin runs and returns its result."""
        plugin = get_plugin("echo")

        self.assertEqual(plugin.run("hello"), "Echo: hello")

    def test_invalid_plugin_raises_clear_error(self):
        """Requesting an unknown plugin raises a clear exception."""
        with self.assertRaises(Exception) as context:
            get_plugin("missing")

        self.assertIn("Plugin not found", str(context.exception))

    def test_cli_plugin_runs_plugin(self):
        """The plugin CLI command loads and runs a plugin."""
        with mock.patch("sys.stdout", new_callable=StringIO) as output:
            exit_code = cli_main(["plugin", "echo", "hello"])

        self.assertEqual(exit_code, 0)
        self.assertIn("Echo: hello", output.getvalue())

    def test_cli_plugin_handles_invalid_plugin(self):
        """The plugin CLI command reports unknown plugins cleanly."""
        with mock.patch("sys.stdout", new_callable=StringIO) as output:
            exit_code = cli_main(["plugin", "missing", "hello"])

        self.assertEqual(exit_code, 1)
        self.assertIn("Error: Plugin not found", output.getvalue())

    def test_cli_score_adds_prompt_history(self):
        """The score CLI command stores scored prompts in history."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)

                with mock.patch("sys.stdout", new_callable=StringIO):
                    exit_code = cli_main(["score", "You are a coach"])
                history = get_history()
            finally:
                os.chdir(original_cwd)

        self.assertEqual(exit_code, 0)
        self.assertEqual(history[0]["prompt"], "You are a coach")

    def test_cli_score_prints_clean_output(self):
        """The score CLI command prints readable scoring output."""
        with mock.patch("arhupy.cli.add_history"):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["score", "You are a fitness coach"])

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Score:", contents)
        self.assertIn("Strengths:", contents)
        self.assertIn("Improvements:", contents)

    def test_cli_score_handles_empty_prompt(self):
        """The score CLI command handles an empty prompt without crashing."""
        with mock.patch("arhupy.cli.add_history"):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["score"])

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Score:", contents)
        self.assertIn("Improvements:", contents)

    def test_compare_prompts_returns_differences(self):
        """compare_prompts returns length, word, common, and unique differences."""
        result = compare_prompts("You are a coach", "You are a helpful assistant")

        self.assertEqual(result["length_diff"], len("You are a coach") - len("You are a helpful assistant"))
        self.assertEqual(result["word_diff"], 4 - 5)
        self.assertEqual(result["common_words"], ["You", "a", "are"])
        self.assertEqual(result["unique_to_p1"], ["coach"])
        self.assertEqual(result["unique_to_p2"], ["assistant", "helpful"])

    def test_cli_diff_prints_comparison_output(self):
        """The diff CLI command prints prompt comparison and scoring output."""
        with mock.patch("arhupy.cli.add_history"):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main([
                    "diff",
                    "You are a fitness coach",
                    "You are a helpful assistant",
                ])

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Length difference:", contents)
        self.assertIn("Word difference:", contents)
        self.assertIn("Common words:", contents)
        self.assertIn("Unique to prompt 1:", contents)
        self.assertIn("Unique to prompt 2:", contents)
        self.assertIn("Prompt 1 score:", contents)
        self.assertIn("Prompt 2 score:", contents)
        self.assertIn("Better prompt:", contents)

    def test_cli_diff_handles_empty_prompts(self):
        """The diff CLI command handles omitted prompts without crashing."""
        with mock.patch("arhupy.cli.add_history"):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["diff"])

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Length difference:", contents)
        self.assertIn("Prompt 1 score:", contents)
        self.assertIn("Prompt 2 score:", contents)
        self.assertIn("Better prompt:", contents)

    def test_cli_improve_prints_original_and_improved_prompt(self):
        """The improve CLI command prints original and improved prompt text."""
        with mock.patch("arhupy.cli.add_history"):
            with mock.patch("arhupy.cli.improve_prompt", return_value="Improved prompt") as improve:
                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    exit_code = cli_main([
                        "improve",
                        "You are a coach",
                        "--api-key",
                        "test-key",
                    ])

        contents = output.getvalue()
        self.assertEqual(exit_code, 0)
        improve.assert_called_once_with("You are a coach", "test-key")
        self.assertIn("Original:", contents)
        self.assertIn("You are a coach", contents)
        self.assertIn("Improved:", contents)
        self.assertIn("Improved prompt", contents)

    def test_cli_improve_handles_missing_api_key_cleanly(self):
        """The improve CLI command reports a clean error when the key is missing."""
        with mock.patch("arhupy.cli.add_history"):
            with mock.patch("sys.stdout", new_callable=StringIO) as output:
                exit_code = cli_main(["improve", "You are a coach"])

        contents = output.getvalue()
        self.assertEqual(exit_code, 1)
        self.assertIn("Error:", contents)
        self.assertIn("API key is required", contents)

    def test_cli_web_calls_run_server(self):
        """The web CLI command starts the local server."""
        with mock.patch("arhupy.cli.run_server") as run_server:
            exit_code = cli_main(["web"])

        self.assertEqual(exit_code, 0)
        run_server.assert_called_once_with()

    def test_cli_storage_commands_save_export_import_and_list(self):
        """Storage CLI commands can save, export, import, and list prompts."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                export_path = os.path.join(temp_dir, "prompts.json")

                with mock.patch("sys.stdout", new_callable=StringIO) as output:
                    self.assertEqual(cli_main(["save", "test", "You are a coach"]), 0)
                    self.assertEqual(cli_main(["export", export_path]), 0)
                    self.assertEqual(cli_main(["import", export_path]), 0)
                    self.assertEqual(cli_main(["list"]), 0)

                contents = output.getvalue()
                self.assertIn("Saved prompt: test", contents)
                self.assertIn("Exported prompts to", contents)
                self.assertIn("Skipped prompts: 1", contents)
                self.assertIn("Saved prompts: 1 prompt", contents)
                self.assertIn("- test", contents)
            finally:
                os.chdir(original_cwd)

    def test_web_render_helpers_include_dashboard_output(self):
        """Web render helpers produce dashboard, scoring, and comparison HTML."""
        page = render_page()
        score = render_score("You are a helpful assistant")
        comparison = render_comparison("You are a coach", "You are a strict coach")

        self.assertIn("arhupy Dashboard", page)
        self.assertIn("Prompt 1", page)
        self.assertIn("Prompt 2", page)
        self.assertIn("Score Prompt", page)
        self.assertIn("Compare Prompts", page)
        self.assertIn("Prompt Score", score)
        self.assertIn("Suggestions", score)
        self.assertIn("Prompt Comparison", comparison)
        self.assertIn("Better prompt", comparison)

    def test_web_can_save_prompt_and_show_saved_prompts(self):
        """The web dashboard can save Prompt 1 and show saved prompts."""
        original_cwd = os.getcwd()
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                os.chdir(temp_dir)
                result = render_save_result("web_prompt", "You are a coach")
                page = render_page()

                self.assertIn("Saved prompt", result)
                self.assertIn("Saved Prompts", page)
                self.assertIn("web_prompt", page)
                self.assertIn("You are a coach", page)
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main()
