"""Local web dashboard for arhupy."""

from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, unquote

from .diff import compare_prompts
from .improver import improve_prompt
from .library import _read_library, save
from .prompt import Prompt
from .scorer import score_prompt
from .share import get_shared


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
        if self.path.startswith("/share/"):
            share_id = unquote(self.path.removeprefix("/share/")).strip()
            self._send_html(render_shared_prompt(share_id))
            return

        self._send_html(render_page())

    def do_POST(self):
        """Handle prompt scoring and comparison form submissions."""
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")
        form = parse_qs(body)
        prompt_1 = form.get("prompt1", [""])[0]
        prompt_2 = form.get("prompt2", [""])[0]
        improve_prompt_text = form.get("improve_prompt", [""])[0]
        api_key = form.get("api_key", [""])[0]
        action = form.get("action", ["score"])[0]
        save_name = form.get("save_name", [""])[0].strip()

        if action == "save":
            result_html = render_save_result(save_name, prompt_1)
            active_tab = "score"
        elif action == "improve":
            result_html = render_improvement(improve_prompt_text, api_key)
            active_tab = "improve"
        elif action == "compare":
            result_html = render_comparison(prompt_1, prompt_2)
            active_tab = "compare"
        elif prompt_1.strip() and prompt_2.strip():
            result_html = render_comparison(prompt_1, prompt_2)
            active_tab = "compare"
        else:
            result_html = render_score(prompt_1)
            active_tab = "score"

        self._send_html(
            render_page(
                prompt_1=prompt_1,
                prompt_2=prompt_2,
                result_html=result_html,
                active_tab=active_tab,
                improve_text=improve_prompt_text,
            )
        )

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


def render_page(prompt_1="", prompt_2="", result_html="", active_tab="score", improve_text=""):
    """Render the dashboard page."""
    score_checked = "checked" if active_tab == "score" else ""
    compare_checked = "checked" if active_tab == "compare" else ""
    improve_checked = "checked" if active_tab == "improve" else ""
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>arhupy Dashboard</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: #f5f7fb;
      color: #18212f;
      font-family: Arial, sans-serif;
      line-height: 1.5;
    }}
    .page {{
      width: min(980px, calc(100% - 32px));
      margin: 0 auto;
      padding: 36px 0;
    }}
    header {{ text-align: center; margin-bottom: 28px; }}
    h1 {{ margin: 0 0 8px; font-size: 2.2rem; }}
    h2, h3 {{ margin-top: 0; }}
    .subtitle {{ margin: 0; color: #5b6678; }}
    .tabs {{
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 16px;
    }}
    .tabs input[type="radio"] {{ display: none; }}
    .tab {{
      border: 1px solid #d5dbea;
      border-radius: 8px 8px 0 0;
      background: #e9edf6;
      padding: 12px;
      text-align: center;
      font-weight: 700;
      cursor: pointer;
    }}
    #tab-score:checked + .tab,
    #tab-compare:checked + .tab,
    #tab-improve:checked + .tab {{
      background: #ffffff;
      border-bottom-color: #ffffff;
      color: #0f5fa8;
    }}
    .tab-panel {{
      display: none;
      grid-column: 1 / -1;
      background: #ffffff;
      border: 1px solid #d5dbea;
      border-radius: 0 0 8px 8px;
      padding: 22px;
      margin-bottom: 18px;
      box-shadow: 0 8px 24px rgba(26, 39, 68, 0.06);
    }}
    #tab-score:checked ~ .score-panel,
    #tab-compare:checked ~ .compare-panel,
    #tab-improve:checked ~ .improve-panel {{
      display: block;
    }}
    form {{
      border: 1px solid #e1e6f0;
      border-radius: 8px;
      padding: 16px;
      background: #fbfcff;
    }}
    label {{ display: block; margin: 12px 0 6px; font-weight: 700; }}
    textarea, input {{
      width: 100%;
      border: 1px solid #c9d1e3;
      border-radius: 6px;
      padding: 10px;
      font: inherit;
      background: #ffffff;
    }}
    textarea {{ min-height: 140px; resize: vertical; }}
    input {{ margin-bottom: 12px; }}
    button {{
      border: 0;
      border-radius: 6px;
      background: #0f5fa8;
      color: #ffffff;
      padding: 10px 14px;
      font-weight: 700;
      cursor: pointer;
    }}
    button.secondary {{ background: #475569; }}
    .output, .saved {{
      background: #ffffff;
      border: 1px solid #d5dbea;
      border-radius: 8px;
      padding: 20px;
      margin-top: 18px;
      box-shadow: 0 8px 24px rgba(26, 39, 68, 0.06);
    }}
    .metric {{
      display: inline-block;
      margin: 0 8px 8px 0;
      padding: 8px 10px;
      border-radius: 6px;
      background: #eef6ff;
      font-weight: 700;
    }}
    ul {{ padding-left: 22px; }}
  </style>
</head>
<body>
  <main class="page">
    <header>
      <h1>arhupy Dashboard</h1>
      <p class="subtitle">Score, compare, improve, and save prompts locally.</p>
    </header>

    <section class="tabs" aria-label="Dashboard tools">
      <input id="tab-score" name="dashboard-tab" type="radio" {score_checked}>
      <label class="tab" for="tab-score">Score</label>
      <input id="tab-compare" name="dashboard-tab" type="radio" {compare_checked}>
      <label class="tab" for="tab-compare">Compare</label>
      <input id="tab-improve" name="dashboard-tab" type="radio" {improve_checked}>
      <label class="tab" for="tab-improve">Improve</label>

      <div class="tab-panel score-panel">
        <form method="post">
          <h2>Score</h2>
          <label for="score_prompt">Prompt</label>
          <textarea id="score_prompt" name="prompt1">{escape(prompt_1)}</textarea>
          <button type="submit" name="action" value="score">Score Prompt</button>
        </form>
      </div>

      <div class="tab-panel compare-panel">
        <form method="post">
          <h2>Compare</h2>
          <label for="compare_prompt1">Prompt 1</label>
          <textarea id="compare_prompt1" name="prompt1">{escape(prompt_1)}</textarea>
          <label for="compare_prompt2">Prompt 2</label>
          <textarea id="compare_prompt2" name="prompt2">{escape(prompt_2)}</textarea>
          <button type="submit" name="action" value="compare">Compare Prompts</button>
        </form>
      </div>

      <div class="tab-panel improve-panel">
        <form method="post">
          <h2>Improve</h2>
          <label for="improve_prompt">Prompt</label>
          <textarea id="improve_prompt" name="improve_prompt">{escape(improve_text)}</textarea>
          <label for="api_key">Claude API Key</label>
          <input id="api_key" name="api_key" type="password" placeholder="YOUR_KEY">
          <button type="submit" name="action" value="improve">Improve Prompt</button>
        </form>
      </div>
    </section>

    <section class="output">
      <h2>Output</h2>
      {result_html or "<p>Choose a tab, enter a prompt, and run an action.</p>"}
    </section>

    <section class="saved">
      <h2>Save Prompt</h2>
      <form method="post">
        <label for="save_prompt">Prompt</label>
        <textarea id="save_prompt" name="prompt1">{escape(prompt_1)}</textarea>
        <label for="save_name">Prompt Name</label>
        <input id="save_name" name="save_name" type="text" placeholder="my_prompt">
        <button class="secondary" type="submit" name="action" value="save">Save Prompt</button>
      </form>
    </section>

    {render_saved_prompts()}
  </main>
</body>
</html>"""


def render_score(prompt):
    """Render scoring results for one prompt."""
    result = score_prompt(prompt)
    strength_items = "".join(
        f"<li>{escape(strength)}</li>" for strength in result["strengths"]
    )
    feedback_items = "".join(
        f"<li>{escape(suggestion)}</li>" for suggestion in result["feedback"]
    )
    return f"""<h3>Prompt Score</h3>
<p class="metric">Score: {result['overall_score']}/10</p>
<p class="metric">Length: {result['length_score']}/10</p>
<p class="metric">Clarity: {result['clarity_score']}/10</p>
<p class="metric">Structure: {result['structure_score']}/10</p>
<h4>Strengths</h4>
<ul>{strength_items}</ul>
<h4>Improvements</h4>
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


def render_improvement(prompt, api_key):
    """Render an improved prompt result."""
    if not prompt.strip():
        return "<p>Please enter a prompt to improve.</p>"
    if not api_key:
        return "<p>Please enter a Claude API key before improving a prompt.</p>"

    try:
        improved = improve_prompt(prompt, api_key)
    except Exception as exc:
        return f"<p>Could not improve prompt: {escape(str(exc))}</p>"

    return f"""<h3>Improved Prompt</h3>
<p><strong>Original:</strong></p>
<p>{escape(prompt)}</p>
<p><strong>Improved:</strong></p>
<p>{escape(improved)}</p>"""


def render_shared_prompt(share_id):
    """Render a shared prompt page."""
    try:
        prompt = get_shared(share_id)
    except Exception as exc:
        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Shared Prompt Not Found</title>
</head>
<body>
  <main>
    <h1>Shared Prompt Not Found</h1>
    <p>{escape(str(exc))}</p>
    <p><a href="/">Back to dashboard</a></p>
  </main>
</body>
</html>"""

    score_html = render_score(prompt)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Shared Prompt</title>
  <style>
    body {{
      margin: 0;
      background: #f5f7fb;
      color: #18212f;
      font-family: Arial, sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(860px, calc(100% - 32px));
      margin: 0 auto;
      padding: 36px 0;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #d5dbea;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 18px;
      box-shadow: 0 8px 24px rgba(26, 39, 68, 0.06);
    }}
    .prompt {{
      white-space: pre-wrap;
      background: #fbfcff;
      border: 1px solid #e1e6f0;
      border-radius: 8px;
      padding: 16px;
    }}
    .metric {{
      display: inline-block;
      margin: 0 8px 8px 0;
      padding: 8px 10px;
      border-radius: 6px;
      background: #eef6ff;
      font-weight: 700;
    }}
  </style>
</head>
<body>
  <main>
    <section class="card">
      <h1>Shared Prompt</h1>
      <p class="prompt">{escape(prompt)}</p>
    </section>
    <section class="card">
      {score_html}
    </section>
    <p><a href="/">Back to dashboard</a></p>
  </main>
</body>
</html>"""


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
        return f"""<section class="saved">
  <h2>Saved Prompts</h2>
  <p>Could not read saved prompts: {message}</p>
</section>"""

    if not prompts:
        return """<section class="saved">
  <h2>Saved Prompts</h2>
  <p>No saved prompts found.</p>
</section>"""

    items = "".join(
        f"<li><strong>{escape(name)}</strong>: {escape(template)}</li>"
        for name, template in sorted(prompts.items())
    )
    return f"""<section class="saved">
  <h2>Saved Prompts</h2>
  <p>{len(prompts)} saved prompt(s)</p>
  <ul>{items}</ul>
</section>"""


def _format_words(words):
    """Format a list of words for HTML output."""
    return ", ".join(words) if words else "None"
