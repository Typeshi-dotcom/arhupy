# arhupy

[![PyPI version](https://img.shields.io/pypi/v/arhupy.svg)](https://pypi.org/project/arhupy/)
[![Python versions](https://img.shields.io/pypi/pyversions/arhupy.svg)](https://pypi.org/project/arhupy/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![GitHub stars](https://img.shields.io/github/stars/Arhu/arhupy.svg?style=social)](https://github.com/Arhu/arhupy)

A lightweight prompt engineering toolkit for LLMs

`arhupy` helps you create, fill, chain, save, version, and estimate prompts for LLMs like Claude, GPT, and Gemini. It is small by design and uses only the Python standard library.

## Installation

Install from PyPI:

```bash
pip install arhupy
```

Install from source:

```bash
git clone https://github.com/Arhu/arhupy.git
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
- Estimate token counts with a simple standard-library helper
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

## Contributing

Contributions are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, test commands, and pull request guidance.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
