# Nexus CLI Assistant

A lightweight CLI tool that provides quick AI-powered answers to Linux, Docker, Ollama, and system administration questions directly from your terminal. Supports local (Ollama) and cloud AI models, with command saving, categorization, history tracking, quick snippets, rate limiting, and caching.

## Features

- 🤖 **Multiple AI Providers**: Ollama (local), OpenAI, Anthropic (Claude), and DeepSeek
- ⚙️ **Easy Provider Switching**: Change default AI provider with a simple command
- 💾 **Command Saving**: Save your favorite commands in organized categories
- 📜 **Command History**: Track your queries for quick access
- ⚡ **Quick Snippets**: Instant access to saved commands without AI processing
- 🚦 **Rate Limiting**: Built-in rate limiting to manage API costs
- 💨 **Caching**: Cache common questions for instant responses
- 🎨 **Structured Output**: Beautiful formatted answers with Commands and Explanation sections
- 📝 **Syntax Highlighting**: Code blocks with proper syntax highlighting
- 🔒 **Virtual Environment**: Isolated Python environment for dependencies

## Installation

### Prerequisites

- Python 3.8 or higher
- pip
- (Optional) Ollama installed and running for local AI

### Quick Install

1. Clone the repository:
```bash
git clone https://github.com/nexus-mike/Nexus-CLI-Assistant.git
cd nexus-cli-assistant
```

2. Run the installation script:
```bash
./scripts/install.sh
```

The script will:
- Create a virtual environment
- Install all dependencies
- Set up the `nexus` command
- Create default configuration

3. Activate the virtual environment:
```bash
source venv/bin/activate
```

4. Test the installation:
```bash
nexus ask "how to check UFW firewall status"
```

### Manual Installation

If you prefer to install manually:

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## Configuration

Configuration is stored in `~/.config/nexus/config.yaml`. The installation script creates a default configuration file.

### Example Configuration

```yaml
ai_provider: ollama  # ollama, openai, anthropic, deepseek
default_model: llama3.2
output_mode: brief

# Rate limiting settings
rate_limiting:
  enabled: true
  requests_per_minute: 30
  requests_per_hour: 500

# Caching settings
cache:
  enabled: true
  ttl_seconds: 3600  # 1 hour
  max_entries: 1000

providers:
  ollama:
    base_url: http://localhost:11434
    model: llama3.2
  
  openai:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o-mini
    rate_limit: 60
  
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-3-5-sonnet-20241022
    rate_limit: 50
  
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    model: deepseek-chat
    base_url: https://api.deepseek.com
    rate_limit: 60
```

### Environment Variables

Set API keys as environment variables:

```bash
export OPENAI_API_KEY="your-key-here"
export ANTHROPIC_API_KEY="your-key-here"
export DEEPSEEK_API_KEY="your-key-here"
```

Or use a `.env` file (copy from `.env.example`).

## Usage

### Ask Questions

Ask a quick question (quotes optional):
```bash
nexus ask "how to check UFW firewall status"
# or without quotes
nexus ask how to check UFW firewall status
```

Get a verbose answer:
```bash
nexus ask --verbose "explain docker networking in detail"
```

### Save Commands

Save a command with category:
```bash
nexus save docker "docker ps -a"
```

Or with the flag:
```bash
nexus save --category docker "docker ps -a"
```

Add a description:
```bash
nexus save docker "docker ps -a" --description "List all containers"
```

### List Saved Commands

List all commands:
```bash
nexus list
```

List by category:
```bash
nexus list docker
# or
nexus list --category docker
```

### Quick Snippets

Quickly access saved commands without AI:
```bash
nexus quick docker
```

### View History

View command history:
```bash
nexus history
```

Limit results:
```bash
nexus history --limit 10
```

### Delete Commands

Delete a saved command:
```bash
nexus delete <command-id>
```

### Configuration

View current configuration:
```bash
nexus config
```

Change default AI provider:
```bash
nexus config --set-provider ollama
nexus config --set-provider openai
nexus config --set-provider anthropic
nexus config --set-provider deepseek
```

The default provider is used for all `nexus ask` commands. You can change it anytime, and the setting persists in your config file.

## Commands Reference

| Command | Description |
|---------|-------------|
| `nexus ask <question>` | Ask a question (quotes optional, checks cache first) |
| `nexus ask --verbose <question>` | Get verbose answer with full details |
| `nexus save <category> <command>` | Save a command with category |
| `nexus save --category <cat> <command>` | Save with category flag |
| `nexus list [--category <cat>]` | List saved commands (optionally filtered) |
| `nexus quick <keyword>` | Quick access to saved commands (no AI) |
| `nexus history [--limit N]` | View command history |
| `nexus delete <id>` | Delete a saved command by ID |
| `nexus config` | Show current configuration |
| `nexus config --set-provider <provider>` | Set default AI provider |

## Virtual Environment

The project uses a virtual environment to isolate dependencies. After installation:

- **Activate**: `source venv/bin/activate`
- **Deactivate**: `deactivate`

### Adding to Shell Profile

To use `nexus` without manually activating the venv, add to your `~/.bashrc` or `~/.zshrc`:

```bash
alias nexus='source /path/to/nexus-cli-assistant/venv/bin/activate && nexus'
```

## Features in Detail

### Structured Output Formatting

Answers are displayed in organized sections:
- **📋 Commands**: Syntax-highlighted code blocks with all detected commands
- **💡 Explanation**: Formatted markdown with full context and details

This makes it easy to quickly find the commands you need while still having access to detailed explanations.

### Default AI Provider

The default AI provider is set in your configuration file (`~/.config/nexus/config.yaml`). By default, it's set to `ollama` for local AI processing. You can change it using:

```bash
nexus config --set-provider <provider>
```

Available providers: `ollama`, `openai`, `anthropic`, `deepseek`

### Command History

All queries are automatically saved to history. View recent queries with `nexus history`.

### Quick Snippets

The `nexus quick` command searches saved commands by keyword, providing instant access without AI processing.

### Rate Limiting

Rate limiting prevents hitting API limits and manages costs. Configure limits in `config.yaml`.

### Caching

Common questions are cached to reduce API calls. Cache settings are configurable in `config.yaml`.

## Database

Commands, history, and cache are stored in SQLite at `~/.config/nexus/data/commands.db`.

## Troubleshooting

### Ollama Connection Issues

If using Ollama, ensure it's running:
```bash
# If running locally
ollama serve

# If running in Docker
docker ps | grep ollama
```

### Ollama Model Not Found

If you get a "model not found" error:

1. Check available models:
```bash
ollama list
# or if in Docker
docker exec ollama-container ollama list
```

2. Update your config file `~/.config/nexus/config.yaml`:
```yaml
providers:
  ollama:
    base_url: http://localhost:11434
    model: your-available-model-name  # Use exact name from ollama list
```

### API Key Issues

Make sure API keys are set as environment variables or in the config file.

### Virtual Environment

If the `nexus` command is not found, activate the virtual environment:
```bash
source venv/bin/activate
```

## Development

### Project Structure

```
nexus-cli-assistant/
├── nexus_qa/          # Main package
│   ├── main.py        # CLI entry point
│   ├── ai_client.py   # AI provider clients
│   ├── storage.py     # Database operations
│   ├── config.py      # Configuration
│   ├── formatter.py   # Output formatting
│   ├── models.py      # Data models
│   ├── cache.py       # Caching system
│   └── rate_limiter.py # Rate limiting
├── config/            # Configuration examples
├── scripts/           # Installation scripts
├── venv/              # Virtual environment
└── requirements.txt   # Dependencies
```

### Running Tests

(Add test instructions when tests are added)

## Contributing

Contributions are welcome! We appreciate your help in making Nexus CLI Assistant better.

Please read our [Contributing Guidelines](CONTRIBUTING.md) before submitting pull requests.

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

For bug reports and feature requests, please use the [GitHub Issues](https://github.com/nexus-mike/Nexus-CLI-Assistant/issues).

## Security

If you discover a security vulnerability, please see our [Security Policy](SECURITY.md) for information on how to report it responsibly.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues and questions:
- Open an issue on [GitHub Issues](https://github.com/nexus-mike/Nexus-CLI-Assistant/issues)
- Check the [Documentation](README.md) for common questions

