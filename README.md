# arhupy

[![PyPI version](https://img.shields.io/pypi/v/arhupy.svg)](https://pypi.org/project/arhupy/)
[![Python versions](https://img.shields.io/pypi/pyversions/arhupy.svg)](https://pypi.org/project/arhupy/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Typeshi-dotcom/arhupy.svg?style=social)](https://github.com/Typeshi-dotcom/arhupy)

A lightweight prompt engineering toolkit for LLMs

`arhupy` helps you create, fill, chain, save, version, and estimate prompts for LLMs like Claude, GPT, and Gemini. It is small by design and uses only the Python standard library.

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

## Quick Start

```python
from arhupy import Prompt

prompt = Prompt("You are a {role}. Speak in {language}.")
print(prompt.fill(role="teacher", language="English"))
```

## Features

- Fill prompt templates with named placeholders
- Chain multiple prompts into one final prompt
- Save and load prompt templates from a local JSON library
- Export and import prompts or prompt chains as shareable JSON files
- Estimate token counts with a simple standard-library helper
- Score prompts with smarter local heuristics and detailed feedback
- Compare prompts and see scoring differences from the CLI
- Improve prompts with Claude through a simple command
- Start faster with built-in prompt templates
- Reuse recent prompts from local history
- Work through prompt actions in interactive mode
- Launch a local web dashboard for scoring and comparison
- Track prompt template versions with notes
- No external dependencies

## CLI Usage

Show available commands:

```bash
arhupy --help
```

Score a prompt:

```bash
arhupy score "You are a fitness coach"
```

Scoring checks prompt length, role clarity, task clarity, placeholders, output format, and constraints.

Compare two prompts:

```bash
arhupy diff "You are a coach" "You are a strict fitness coach"
```

Improve a prompt:

```bash
arhupy improve "You are a coach" --api-key YOUR_KEY
```

Save, list, export, and import prompts:

```bash
arhupy save my_prompt "You are a coach"
arhupy list
arhupy export prompts.json
arhupy import prompts.json
```

Start the local web dashboard:

```bash
arhupy web
```

List and view built-in templates:

```bash
arhupy templates
arhupy template coding
```

Show and reuse recent prompts:

```bash
arhupy history
arhupy history 5
arhupy reuse 2
arhupy reuse 2 --score
```

Start interactive mode:

```bash
arhupy interactive
```

Fill a built-in template:

```bash
arhupy fill coding
```

Build a prompt chain:

```bash
arhupy chain
```

Compare prompts from history:

```bash
arhupy compare-history 1 2
```

## Examples

### Prompt

```python
from arhupy import Prompt

prompt = Prompt("You are a {role}. Speak in {language}.")
filled = prompt.fill(role="coding assistant", language="English")

print(filled)
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

### Library Save And Load

```python
from arhupy import Prompt, load, save

prompt = Prompt("Summarize this in {style}: {text}")
save("summarizer", prompt)

loaded = load("summarizer")
print(loaded.fill(style="plain English", text="Prompt engineering is useful."))
```

Saved prompts are stored in `arhupy_library.json` in your current working directory.

### Token Estimation

```python
from arhupy import estimate_tokens

tokens = estimate_tokens("A short prompt for an LLM.")
print(tokens)
```

## Prompt Scoring

```bash
arhupy score "You are a fitness coach"
```

## Smart Prompt Scoring

`arhupy` scores prompts with readable local heuristics. It looks for a useful length, a clear role, a direct task, reusable placeholders, output instructions, and constraints.

```bash
arhupy score "You are a {role}. Explain {task} step by step in bullet points within 200 words only."
```

Example output:

```text
Score: 9/10

Strengths:
- Good prompt length
- Role is defined
- Clear task defined

Improvements:
- Prompt looks strong and ready to use.
```

## Prompt Comparison

```bash
arhupy diff "You are a fitness coach" "You are a helpful assistant"
```

## Prompt Templates

Use built-in templates for common prompt patterns:

```bash
arhupy templates
arhupy template fitness
```

In Python:

```python
from arhupy import Prompt, get_template, list_templates

print(list_templates())

template = get_template("coding")
prompt = Prompt(template)
print(prompt.fill(concept="recursion"))
```

## Template Autofill

Fill a built-in template from the terminal. `arhupy` asks for each placeholder and prints the completed prompt.

```bash
arhupy fill coding
```

In Python:

```python
from arhupy import fill_template

prompt = fill_template("fitness")
print(prompt)
```

## Prompt Chaining

Combine multiple prompt steps into one workflow-style prompt:

```bash
arhupy chain
```

Enter each prompt step when asked. Submit an empty line to finish and print the final combined prompt.

In Python:

```python
from arhupy import build_chain

chain = build_chain([
    "System: Be concise.",
    "User: Explain recursion.",
])
print(chain)
```

## History Comparison

Compare two saved history prompts by their history indexes:

```bash
arhupy history
arhupy compare-history 1 2
```

`arhupy` prints both prompts, their differences, a score comparison, and which prompt looks stronger.

In Python:

```python
from arhupy import add_history, compare_history

add_history("You are a coach.")
add_history("You are a fitness coach. Explain warmups step by step.")
print(compare_history(1, 2))
```

## Prompt History

`arhupy` stores prompts from `score`, `diff`, and `improve` commands in `arhupy_history.json` in your current working directory.

```bash
arhupy score "You are a coach. Explain warmups step by step."
arhupy history
arhupy history 5
arhupy reuse 1
arhupy reuse 1 --score
```

In Python:

```python
from arhupy import add_history, get_history, get_prompt_by_index

add_history("You are a coach. Explain progressive overload.")
print(get_history(limit=1))
print(get_prompt_by_index(1))
```

## Interactive Mode

Run an interactive prompt workflow from the terminal:

```bash
arhupy interactive
```

Interactive mode lets you enter one prompt, then score it, improve it, compare it with another prompt, save it to the prompt library, or exit.

## Web Dashboard

```bash
arhupy web
```

This starts a local dashboard at `http://localhost:8000`.

## Saving and Sharing Prompts

```bash
arhupy save my_prompt "You are a coach"
arhupy export prompts.json
arhupy import prompts.json
arhupy list
```

## AI Prompt Improvement

```bash
arhupy improve "You are a coach" --api-key YOUR_KEY
```

Use a real Claude API key for live AI improvement. The `YOUR_KEY` placeholder runs a local demo improvement so the command can be tested safely.

## Claude Integration

```python
from arhupy import Prompt, ClaudeClient

client = ClaudeClient(api_key="your-api-key")

prompt = Prompt("You are a {role}. Answer this: {question}")
response = client.ask_with_template(prompt, role="fitness coach", question="What is progressive overload?")
print(response)
```

## Export and Import

Save a prompt to JSON:

```python
from arhupy import Prompt, export_prompt

prompt = Prompt("Write a {tone} email about {topic}.")
prompt.fill(tone="friendly", topic="a project update")

export_prompt(prompt, "email_prompt.json")
```

Load a prompt from JSON:

```python
from arhupy import import_prompt

prompt = import_prompt("email_prompt.json")
print(prompt)
```

Save a prompt chain to JSON:

```python
from arhupy import Prompt, PromptChain, export_chain

system = Prompt("System: {instruction}")
user = Prompt("User: {request}")
system.fill(instruction="Be concise.")
user.fill(request="Summarize this report.")

chain = PromptChain([system, user])
export_chain(chain, "summary_chain.json")
```

Load a prompt chain from JSON:

```python
from arhupy import import_chain

chain = import_chain("summary_chain.json")
print(chain.build())
```

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, test commands, and pull request guidance.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
