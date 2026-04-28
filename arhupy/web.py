"""Local web dashboard for arhupy."""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs

from .diff import compare_prompts
from .library import _read_library, save
from .prompt import Prompt
from .scorer import score_prompt


def run_server(host="localhost", port=8000):
    """Start the local arhupy web dashboard server."""
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"Server running at http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
    finally:
        server.server_close()


class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the local dashboard."""

    def do_GET(self):
        """Serve the dashboard HTML page."""
        self._send_html(render_page())

    def do_POST(self):
        """Handle prompt scoring and comparison form submissions."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(body)
        prompt_1 = form.get("prompt1", [""])[0]
        prompt_2 = form.get("prompt2", [""])[0]
        action = form.get("action", ["score"])[0]
        save_name = form.get("save_name", [""])[0].strip()

        if action == "save":
            result_html = render_save_result(save_name, prompt_1)
        elif prompt_1.strip() and prompt_2.strip():
            result_html = render_comparison(prompt_1, prompt_2)
        else:
            result_html = render_score(prompt_1)

        self._send_html(render_page(prompt_1, prompt_2, result_html))

    def log_message(self, format, *args):
        """Silence default request logging to keep CLI output clean."""
        return

    def _send_html(self, html):
        """Send an HTML response to the browser."""
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def render_page(prompt_1="", prompt_2="", result_html=""):
    """Render the dashboard page."""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>arhupy Dashboard</title>
  <style>
    body {{ font-family: Arial, sans-serif; max-width: 900px; margin: 40px auto; padding: 0 20px; line-height: 1.5; }}
    textarea {{ width: 100%; min-height: 120px; margin: 8px 0 16px; padding: 10px; font: inherit; }}
    button {{ margin-right: 8px; padding: 8px 14px; cursor: pointer; }}
    .output {{ margin-top: 24px; padding: 16px; border: 1px solid #ddd; background: #fafafa; }}
  </style>
</head>
<body>
  <h1>arhupy Dashboard</h1>
  <form method="post">
    <label for="prompt1">Prompt 1</label>
    <textarea id="prompt1" name="prompt1">{escape(prompt_1)}</textarea>

    <label for="prompt2">Prompt 2</label>
    <textarea id="prompt2" name="prompt2">{escape(prompt_2)}</textarea>

    <label for="save_name">Save Prompt 1 As</label>
    <input id="save_name" name="save_name" type="text" placeholder="my_prompt">

    <button type="submit" name="action" value="score">Score Prompt</button>
    <button type="submit" name="action" value="compare">Compare Prompts</button>
    <button type="submit" name="action" value="save">Save Prompt</button>
  </form>

  <div class="output">
    <h2>Output</h2>
    {result_html or "<p>Enter a prompt and choose an action.</p>"}
  </div>

  {render_saved_prompts()}
</body>
</html>"""


def render_score(prompt):
    """Render scoring results for one prompt."""
    result = score_prompt(prompt)
    feedback_items = "".join(
        f"<li>{escape(suggestion)}</li>" for suggestion in result["feedback"]
    )
    return f"""<h3>Prompt Score</h3>
<p><strong>Score:</strong> {result['overall_score']}/10</p>
<p><strong>Length:</strong> {result['length_score']}/10</p>
<p><strong>Clarity:</strong> {result['clarity_score']}/10</p>
<p><strong>Structure:</strong> {result['structure_score']}/10</p>
<h4>Suggestions</h4>
<ul>{feedback_items}</ul>"""


def render_comparison(prompt_1, prompt_2):
    """Render comparison results for two prompts."""
    result = compare_prompts(prompt_1, prompt_2)
    score_1 = score_prompt(prompt_1)["overall_score"]
    score_2 = score_prompt(prompt_2)["overall_score"]
    if score_1 > score_2:
        better_prompt = "Prompt 1"
    elif score_2 > score_1:
        better_prompt = "Prompt 2"
    else:
        better_prompt = "Tie"

    return f"""<h3>Prompt Comparison</h3>
<p><strong>Length difference:</strong> {result['length_diff']}</p>
<p><strong>Word difference:</strong> {result['word_diff']}</p>
<p><strong>Common words:</strong> {escape(_format_words(result['common_words']))}</p>
<p><strong>Unique to prompt 1:</strong> {escape(_format_words(result['unique_to_p1']))}</p>
<p><strong>Unique to prompt 2:</strong> {escape(_format_words(result['unique_to_p2']))}</p>
<p><strong>Prompt 1 score:</strong> {score_1}/10</p>
<p><strong>Prompt 2 score:</strong> {score_2}/10</p>
<p><strong>Better prompt:</strong> {better_prompt}</p>"""


def render_save_result(name, prompt):
    """Save Prompt 1 and render a readable result message."""
    if not name:
        return "<p>Please enter a name before saving a prompt.</p>"
    if not prompt.strip():
        return "<p>Please enter Prompt 1 before saving.</p>"

    save(name, Prompt(prompt))
    return f"<p>Saved prompt: <strong>{escape(name)}</strong></p>"


def render_saved_prompts():
    """Render saved prompts from the local prompt library."""
    try:
        prompts = _read_library()
    except Exception as exc:
        message = escape(str(exc))
        return f"""<section>
  <h2>Saved Prompts</h2>
  <p>Could not read saved prompts: {message}</p>
</section>"""

    if not prompts:
        return """<section>
  <h2>Saved Prompts</h2>
  <p>No saved prompts found.</p>
</section>"""

    items = "".join(
        f"<li><strong>{escape(name)}</strong>: {escape(template)}</li>"
        for name, template in sorted(prompts.items())
    )
    return f"""<section>
  <h2>Saved Prompts</h2>
  <p>{len(prompts)} saved prompt(s)</p>
  <ul>{items}</ul>
</section>"""


def _format_words(words):
    """Format a list of words for HTML output."""
    return ", ".join(words) if words else "None"
