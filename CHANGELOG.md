# Changelog

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
