# arhupy

[![PyPI version](https://img.shields.io/pypi/v/arhupy.svg)](https://pypi.org/project/arhupy/)
[![Python versions](https://img.shields.io/pypi/pyversions/arhupy.svg)](https://pypi.org/project/arhupy/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg)](pyproject.toml)
[![GitHub stars](https://img.shields.io/github/stars/Typeshi-dotcom/arhupy.svg?style=social)](https://github.com/Typeshi-dotcom/arhupy)

A lightweight prompt engineering toolkit for LLMs like Claude, GPT, and Gemini.

`arhupy` gives you a practical set of tools for writing, scoring, comparing, saving, exporting, improving, and reusing prompts. It works from both Python and the command line, uses only the Python standard library, and stores local data as simple JSON files in your current working directory.

```text
Write prompt -> Score it -> Compare versions -> Save or export -> Reuse later
                         -> Improve with Claude
                         -> Serve through CLI, web, or local API
```

## Why arhupy?

Prompt engineering can get messy fast. `arhupy` keeps the useful parts small and organized:

| Need | arhupy gives you |
| --- | --- |
| Fill reusable prompts | `Prompt("You are a {role}")` |
| Chain prompt steps | `PromptChain` and `arhupy chain` |
| Score prompt quality | `score_prompt()` and `arhupy score` |
| Compare prompt versions | `compare_prompts()` and `arhupy diff` |
| Save prompt libraries | Local `arhupy_library.json` storage |
| Share prompts | JSON export and import helpers |
| Track sessions | Local prompt history with reuse |
| Improve with AI | Claude-powered prompt improvement |
| Run locally | CLI, web dashboard, and HTTP API |
| Extend behavior | Simple plugin system |

## Installation

Install from PyPI:

```bash
pip install arhupy
```

Install from source:

```bash
git clone https://github.com/Typeshi-dotcom/arhupy.git
cd arhupy
pip install -e .
```

Check the CLI:

```bash
arhupy --help
```

## Quick Start

```python
from arhupy import Prompt

prompt = Prompt("You are a {role}. Explain {topic} in {style}.")
filled = prompt.fill(
    role="fitness coach",
    topic="progressive overload",
    style="simple terms",
)

print(filled)
```

Output:

```text
You are a fitness coach. Explain progressive overload in simple terms.
```

## Feature Map

| Feature | Python API | CLI command |
| --- | --- | --- |
| Prompt templates | `Prompt` | `arhupy fill coding` |
| Prompt chains | `PromptChain`, `build_chain()` | `arhupy chain` |
| Prompt scoring | `score_prompt()` | `arhupy score "..."` |
| Prompt comparison | `compare_prompts()` | `arhupy diff "..." "..."` |
| Prompt storage | `save()`, `load()` | `arhupy save`, `arhupy list` |
| Sharing | `export_prompt()`, `import_prompt()` | `arhupy export`, `arhupy import` |
| History | `add_history()`, `get_history()` | `arhupy history`, `arhupy reuse` |
| Claude integration | `ClaudeClient`, `improve_prompt()` | `arhupy improve` |
| Web dashboard | `run_server()` | `arhupy web` |
| Local API | `run_api_server()` | `arhupy api` |
| Plugins | `ArhupyPlugin`, `get_plugin()` | `arhupy plugin echo "hello"` |

## CLI Command Reference

### Score a prompt

```bash
arhupy score "You are a fitness coach. Explain progressive overload step by step."
```

What it checks:

| Check | What it looks for |
| --- | --- |
| Length | Too short, ideal length, or too long |
| Role | Phrases like `you are`, `act as`, or `role` |
| Task clarity | Words like `write`, `explain`, `generate`, `analyze`, or `give` |
| Structure | Placeholders like `{role}`, `{task}`, or `{question}` |
| Output format | Instructions like `bullet points`, `step by step`, or `format` |
| Constraints | Words like `limit`, `max`, `within`, or `only` |

Example output:

```text
Score: 8/10

Strengths:
- Good prompt length
- Role is defined
- Clear task defined

Improvements:
- Use placeholders like {role}, {task}, or {question}.
```

### Compare two prompts

```bash
arhupy diff "You are a coach" "You are a strict fitness coach"
```

The comparison shows:

- Length difference
- Word count difference
- Common words
- Words unique to each prompt
- Score for each prompt
- Which prompt looks stronger

### Improve a prompt with Claude

```bash
arhupy improve "You are a coach" --api-key YOUR_KEY
```

`arhupy` uses the built-in `ClaudeClient` with `urllib`, so no external request library is needed. For safe local testing, the placeholder `YOUR_KEY` returns a demo improvement without making a real API call.

### Save, list, export, and import prompts

```bash
arhupy save workout "You are a fitness coach. Create a {plan} for {goal}."
arhupy list
arhupy export prompts.json
arhupy import prompts.json
```

Saved prompts live in:

```text
arhupy_library.json
```

The file is created in your current working directory.

### Use built-in templates

```bash
arhupy templates
arhupy template coding
arhupy fill coding
```

Built-in templates:

| Name | Template |
| --- | --- |
| `fitness` | `You are a fitness coach. Create a {plan} for {goal}.` |
| `coding` | `You are a senior developer. Explain {concept} in simple terms.` |
| `writing` | `You are a writer. Write a {type} about {topic}.` |
| `business` | `You are a business expert. Analyze {idea} and suggest improvements.` |

### Build a prompt chain

```bash
arhupy chain
```

Enter one prompt per line. Submit an empty line to finish.

Example:

```text
Enter prompt 1: You are a coach.
Enter prompt 2: Explain progressive overload.
Enter prompt 3: Use bullet points.
Enter prompt 4:
```

Output:

```text
You are a coach.
Explain progressive overload.
Use bullet points.
```

### Work with prompt history

Commands that score, diff, or improve prompts automatically save them to history.

```bash
arhupy history
arhupy history 5
arhupy reuse 1
arhupy reuse 1 --score
arhupy compare-history 1 2
```

History lives in:

```text
arhupy_history.json
```

### Export and import session history

```bash
arhupy export-history history.json
arhupy import-history history.json
```

Imported history entries are merged safely. Duplicate entries are skipped.

### Start interactive mode

```bash
arhupy interactive
```

Interactive mode lets you choose actions from a menu:

```text
1. Score prompt
2. Improve prompt
3. Compare with another prompt
4. Save prompt
5. Exit
6. Fill template
7. Build prompt chain
8. Compare history prompts
9. Export history
10. Import history
```

### Start the web dashboard

```bash
arhupy web
```

Then open:

```text
http://localhost:8000
```

The dashboard includes:

- Score, Compare, and Improve tabs
- Prompt scoring with strengths and improvements
- Prompt comparison
- AI prompt improvement with a Claude API key field
- Saved prompt display
- Save prompt button

## Improved Web Dashboard

The local dashboard uses only Python's standard-library `http.server`, but gives you a cleaner browser interface for day-to-day prompt work.

```bash
arhupy web
```

Open `http://localhost:8000` and use:

| Tab | Inputs | Output |
| --- | --- | --- |
| Score | One prompt textarea | Score, strengths, and improvements |
| Compare | Two prompt textareas | Differences, prompt scores, and better prompt |
| Improve | Prompt textarea plus API key field | Claude-improved prompt text |

### Start API mode

```bash
arhupy api
```

Then call the local API at:

```text
http://localhost:8001
```

Endpoints:

| Endpoint | Method | Body |
| --- | --- | --- |
| `/score` | `POST` | `{ "prompt": "You are a coach" }` |
| `/diff` | `POST` | `{ "p1": "Prompt one", "p2": "Prompt two" }` |
| `/improve` | `POST` | `{ "prompt": "You are a coach", "api_key": "YOUR_KEY" }` |

Example with curl on macOS/Linux:

```bash
curl -X POST http://localhost:8001/score \
  -H "Content-Type: application/json" \
  -d '{"prompt":"You are a coach"}'
```

Example with curl on Windows PowerShell:

```powershell
curl.exe -X POST "http://localhost:8001/score" -H "Content-Type: application/json" --data-raw '{""prompt"":""You are a coach""}'
```

### Run a plugin

```bash
arhupy plugin echo "hello"
```

Output:

```text
Echo: hello
```

## Python API Examples

### Prompt

```python
from arhupy import Prompt

prompt = Prompt("You are a {role}. Speak in {language}.")

print(prompt.fill(role="coding assistant", language="English"))
prompt.preview()
prompt.reset()
```

### PromptChain

```python
from arhupy import Prompt, PromptChain

system = Prompt("System: {instruction}")
user = Prompt("User: {task}")

system.fill(instruction="Be concise and practical.")
user.fill(task="Explain prompt chaining.")

chain = PromptChain([system, user])
print(chain.build())
```

### Simple prompt chain from strings

```python
from arhupy import build_chain

final_prompt = build_chain([
    "You are a senior developer.",
    "Explain recursion in simple terms.",
    "Use one short example.",
])

print(final_prompt)
```

### Prompt scoring

```python
from arhupy import score_prompt

result = score_prompt(
    "You are a {role}. Explain {task} step by step in bullet points within 200 words only."
)

print(result["overall_score"])
print(result["strengths"])
print(result["feedback"])
```

### Prompt comparison

```python
from arhupy import compare_prompts

result = compare_prompts(
    "You are a coach",
    "You are a strict fitness coach",
)

print(result)
```

### Save and load prompts

```python
from arhupy import Prompt, load, save

prompt = Prompt("Summarize this in {style}: {text}")
save("summarizer", prompt)

loaded = load("summarizer")
print(loaded.fill(style="plain English", text="Prompt engineering is useful."))
```

### Export and import one prompt

```python
from arhupy import Prompt, export_prompt, import_prompt

prompt = Prompt("Write a {tone} email about {topic}.")
prompt.fill(tone="friendly", topic="a project update")

export_prompt(prompt, "email_prompt.json")
restored = import_prompt("email_prompt.json")

print(restored)
```

### Export and import a prompt chain

```python
from arhupy import Prompt, PromptChain, export_chain, import_chain

system = Prompt("System: {instruction}")
user = Prompt("User: {request}")

system.fill(instruction="Be concise.")
user.fill(request="Summarize this report.")

chain = PromptChain([system, user])
export_chain(chain, "summary_chain.json")

restored = import_chain("summary_chain.json")
print(restored.build())
```

### Token estimation

```python
from arhupy import estimate_tokens

tokens = estimate_tokens("A short prompt for an LLM.")
print(tokens)
```

### Built-in templates

```python
from arhupy import Prompt, get_template, list_templates

print(list_templates())

template = get_template("coding")
prompt = Prompt(template)
print(prompt.fill(concept="recursion"))
```

### Prompt history

```python
from arhupy import add_history, get_history, get_prompt_by_index

add_history("You are a coach. Explain progressive overload.")

print(get_history(limit=1))
print(get_prompt_by_index(1))
```

### History comparison

```python
from arhupy import add_history, compare_history

add_history("You are a coach.")
add_history("You are a fitness coach. Explain warmups step by step.")

print(compare_history(1, 2))
```

### Claude integration

```python
from arhupy import Prompt, ClaudeClient

client = ClaudeClient(api_key="your-api-key")

prompt = Prompt("You are a {role}. Answer this: {question}")
response = client.ask_with_template(
    prompt,
    role="fitness coach",
    question="What is progressive overload?",
)

print(response)
```

### AI prompt improvement

```python
from arhupy import improve_prompt

improved = improve_prompt("You are a coach", api_key="your-api-key")
print(improved)
```

### Plugin system

Bundled echo plugin:

```python
from arhupy import get_plugin

plugin = get_plugin("echo")
print(plugin.run("hello"))
```

Create a new plugin inside `arhupy/plugins/`:

```python
from arhupy.plugins import ArhupyPlugin


class EchoPlugin(ArhupyPlugin):
    name = "echo"

    def run(self, text):
        return f"Echo: {text}"
```

## Local Files Created By arhupy

`arhupy` keeps local project data in your current working directory:

| File | Purpose |
| --- | --- |
| `arhupy_library.json` | Saved prompt templates |
| `arhupy_versions.json` | Versioned prompt snapshots |
| `arhupy_history.json` | Prompt history |

These files are ignored by the included `.gitignore` so private prompt data does not get committed by accident.

## Design Goals

- No external runtime dependencies
- Beginner-friendly Python APIs
- Simple JSON storage
- Clear command-line output
- Local-first workflows
- Easy GitHub and PyPI publishing
- Extensible plugin architecture

## Development

Clone and install in editable mode:

```bash
git clone https://github.com/Typeshi-dotcom/arhupy.git
cd arhupy
pip install -e .
```

Run tests:

```bash
python -m unittest
```

Build package artifacts:

```bash
python -m build
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, test commands, and pull request guidance.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
