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
- Score prompts and get simple feedback from local heuristics
- Track prompt template versions with notes
- No external dependencies

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

## Prompt Comparison

```bash
arhupy diff "You are a fitness coach" "You are a helpful assistant"
```

## Web Dashboard

```bash
arhupy web
```

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
