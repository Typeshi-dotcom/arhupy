# Changelog

## [2.2.0] - Shareable Links

### Added

- Ability to share prompts via local links

## [2.1.0] - UI Upgrade

### Added

- Improved web dashboard layout and usability

## [2.0.0] - Plugin System

### Added

- Plugin support for extending arhupy

### Changed

- Expanded README with detailed command usage, API examples, and PyPI-friendly visual tables

## [1.9.0] - API Mode

### Added

- Local HTTP API for scoring, diff, improve

## [1.8.0] - Session Export

### Added

- Export/import for prompt history

## [1.7.0] - History Comparison

### Added

- Comparison of prompts from history

## [1.6.0] - Prompt Chaining

### Added

- Ability to combine prompts into workflows

## [1.5.0] - Template Autofill

### Added

- Interactive template filling

## [1.4.0] - Interactive Mode

### Added

- Interactive CLI session

## [1.3.0] - Prompt History

### Added

- Prompt history tracking and reuse

## [1.2.0] - Prompt Templates

### Added

- Added built-in prompt templates

## [1.1.0] - Smart Scoring

### Added

- Strengths and detailed prompt feedback

### Changed

- Improved scoring logic for length, role, task clarity, structure, output format, and constraints

## [1.0.0] - Initial PyPI Release

### Changed

- Prepared package metadata, documentation, and CLI examples for PyPI
- Marked the project as production-ready

## [0.9.0] - AI Prompt Improvement

### Added

- AI-powered prompt improvement

## [0.8.0] - Storage Improvements

### Added

- `export_all()` and `import_all()`
- CLI export and import commands
- Improved prompt storage system

## [0.7.0] - Web Dashboard

### Added

- Local web interface for scoring and comparing prompts

## [0.6.0] - Prompt Comparison

### Added

- Prompt diff and comparison tool

## [0.5.0] - Prompt Scoring

### Added

- Prompt scoring and feedback system

## [0.3.0] - Export and Import

### Added

- `Prompt.to_dict()` and `Prompt.from_dict()`
- `PromptChain.to_dict()` and `PromptChain.from_dict()`
- `export_prompt()`, `import_prompt()`, `export_chain()`, and `import_chain()`

## [0.2.0] - Claude API Integration

### Added

- `ClaudeClient` class
- `ask()` method for sending filled prompt strings to Claude
- `ask_with_template()` method for filling `Prompt` objects before sending them to Claude

## [0.1.0] - Initial Release

### Added

- `Prompt` class for template filling, previewing, resetting, and string output
- `PromptChain` class for joining multiple prompts
- Local JSON prompt library with save, load, list, and delete helpers
- Simple token estimation helper
- Prompt version history helpers
- Unit tests using Python's built-in `unittest` module
- Project metadata for packaging and open source distribution
