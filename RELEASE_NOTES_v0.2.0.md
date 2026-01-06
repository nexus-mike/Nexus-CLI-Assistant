# Release Notes - v0.2.0

## What's New

### 🎨 Enhanced Output Formatting
- **Structured Sections**: Answers now display in organized sections:
  - 📋 **Commands**: Syntax-highlighted code blocks with all detected commands
  - 💡 **Explanation**: Formatted markdown with full context
- Beautiful bordered panels make answers stand out
- Better visual hierarchy and readability

### 🔍 Improved Command Detection
- Automatically extracts commands from:
  - Numbered lists (1. `docker ps`)
  - Code blocks (```bash ... ```)
  - Inline backticks (`docker ps`)
  - Plain text command lines
- Smarter pattern matching for better command recognition

### 💬 Better Question Handling
- **No quotes needed**: Ask questions naturally without quotes
  - `nexus ask how to check docker status` ✅
  - `nexus ask "how to check docker status"` ✅ (still works)
- Automatic word joining for multi-word questions

### ⚙️ Configuration Management
- **Set Default Provider**: Easily change your default AI provider
  ```bash
  nexus config --set-provider ollama
  nexus config --set-provider openai
  ```
- Enhanced configuration display showing current default provider
- Provider validation to ensure only configured providers can be set

### 🎯 Other Improvements
- Enhanced syntax highlighting for code blocks
- Better markdown rendering in explanations
- Improved error messages and user feedback
- Questions can be asked without quotes (automatic word joining)

## Installation

Update from v0.1.0:
```bash
cd nexus-cli-assistant
git pull
source venv/bin/activate
pip install -e .
```

Or fresh install:
```bash
git clone https://github.com/nexus-mike/Nexus-CLI-Assistant.git
cd nexus-cli-assistant
./scripts/install.sh
```

## Breaking Changes

None - this is a backward-compatible update.

## Contributors

- Maikel van den Brink

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

