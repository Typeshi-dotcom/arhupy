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
    compare_prompts,
    estimate_tokens,
    export_all,
    export_chain,
    export_prompt,
    get_template,
    get_history,
    get_prompt_by_index,
    improve_prompt,
    import_all,
    import_chain,
    import_prompt,
    list_all,
    list_templates,
    load,
    run_interactive,
    save,
    save_version,
    score_prompt,
)
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

    def test_cli_interactive_calls_run_interactive(self):
        """The interactive CLI command starts interactive mode."""
        with mock.patch("arhupy.cli.run_interactive") as interactive:
            exit_code = cli_main(["interactive"])

        self.assertEqual(exit_code, 0)
        interactive.assert_called_once_with()

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
