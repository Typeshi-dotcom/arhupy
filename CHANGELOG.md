# Changelog

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
