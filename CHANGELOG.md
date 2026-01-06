# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2025-01-06

### Added
- Structured output formatting with Commands and Explanation sections
- Enhanced command parsing from AI responses (numbered lists, backticks, inline code)
- Support for questions without quotes (automatic word joining)
- Improved syntax highlighting for code blocks
- Better visual presentation with bordered panels
- `nexus config --set-provider <provider>` command to change default AI provider
- Enhanced configuration display showing current default provider

### Improved
- Command extraction now handles multiple formats (numbered lists, backticks, code blocks)
- Better pattern matching for command detection
- Enhanced explanation formatting with markdown support
- Configuration management with easy provider switching

## [0.1.0] - 2024-01-06

### Added
- Initial release of Nexus CLI Assistant
- Support for multiple AI providers (Ollama, OpenAI, Anthropic, DeepSeek)
- Command saving and categorization
- Command history tracking
- Quick snippets for instant command access
- Rate limiting for API calls
- Response caching with TTL
- Brief and verbose output modes
- Rich terminal output formatting
- SQLite database for commands, history, and cache
- Configuration management with YAML
- Virtual environment support
- Installation script

[Unreleased]: https://github.com/nexus-mike/Nexus-CLI-Assistant/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/nexus-mike/Nexus-CLI-Assistant/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/nexus-mike/Nexus-CLI-Assistant/releases/tag/v0.1.0

