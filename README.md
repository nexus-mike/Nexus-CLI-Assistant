# Nexus CLI Assistant

A lightweight CLI tool that provides quick AI-powered answers to Linux, Docker, Ollama, and system administration questions directly from your terminal. Get instant code snippets, commands, and solutions without leaving your bash shell. Supports local (Ollama) and cloud AI models, with command saving, categorization, history tracking, quick snippets, rate limiting, and caching.

## Features

- 🤖 **Multiple AI Providers**: Ollama (local), OpenAI, Anthropic (Claude), and DeepSeek
- ⚡ **Quick Code Generation**: Get instant code snippets, scripts, and commands directly in your terminal
- ⚙️ **Easy Provider Switching**: Change default AI provider with a simple command
- 💾 **Command Saving**: Save your favorite commands in organized categories
- 📜 **Command History**: Track your queries for quick access
- 🔍 **Quick Snippets**: Instant access to saved commands without AI processing
- 🚦 **Rate Limiting**: Built-in rate limiting to manage API costs
- 💨 **Caching**: Cache common questions for instant responses
- 🎨 **Structured Output**: Beautiful formatted answers with Commands and Explanation sections
- 📝 **Syntax Highlighting**: Code blocks with proper syntax highlighting
- 🔒 **Virtual Environment**: Isolated Python environment for dependencies
- 🐛 **Error Debugging**: Debug error messages instantly without leaving your terminal
- 📖 **Command Explanation**: Understand complex commands with detailed breakdowns
- 🛡️ **Safety Checks**: Verify command safety before execution
- 📜 **Script Generation**: Generate production-ready scripts with best practices
- 🔄 **Workflow Automation**: Automate repetitive tasks with pre-built workflow templates
- 🎬 **YouTube Transcription**: Transcribe YouTube videos to text using local Whisper AI

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
- Install workflow templates

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
    model: llama3.2  # Free and local - no API costs!
  
  openai:
    api_key: ${OPENAI_API_KEY}
    model: gpt-4o-mini  # Recommended: gpt-5.2 (latest), gpt-4o-mini (cost-effective), or gpt-4o (high quality)
    rate_limit: 60
  
  anthropic:
    api_key: ${ANTHROPIC_API_KEY}
    model: claude-3.5-sonnet-20241022  # Recommended: claude-4-sonnet (latest), claude-4-opus (premium), or claude-3.5-sonnet (stable)
    rate_limit: 50
  
  deepseek:
    api_key: ${DEEPSEEK_API_KEY}
    model: deepseek-chat  # Recommended: deepseek-chat or deepseek-coder
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

### AI Models and Recommendations

#### Choosing the Right Model for Code Generation

Different AI providers offer various models optimized for different use cases. Here's a guide to help you choose:

##### **Ollama (Free & Local)**
- **Best for**: Privacy, offline use, no API costs
- **Recommended models**:
  - `llama3.2` - Good general purpose, fast (default)
  - `llama3.1` - Better reasoning, slightly slower
  - `codellama` - Specialized for code generation
  - `mistral` or `mixtral` - Excellent code quality
- **Cost**: Free (runs locally on your machine)
- **Setup**: [Install Ollama](https://ollama.ai/download)

##### **OpenAI (Premium)**
- **Best for**: High-quality code generation, complex tasks
- **Recommended models for code**:
  - **`gpt-5.2`** - ⭐ Latest model, best quality, excellent for complex code (latest, premium)
    - Cost: ~$1.75 per 1M input tokens, ~$14 per 1M output tokens
    - Best for: Complex scripts, production code, advanced debugging
    - Features: Updated knowledge, improved coding capabilities
  - **`gpt-4o`** - ⭐ High quality, excellent for complex code generation
    - Cost: ~$2.50-5.00 per 1M input tokens, ~$10-15 per 1M output tokens
    - Best for: Complex scripts, production code, debugging
  - **`gpt-4o-mini`** - ⭐ Recommended balance of quality and cost
    - Cost: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens
    - Best for: Most code generation tasks, quick scripts
  - `gpt-4-turbo` - High quality, good for complex code
    - Cost: ~$10 per 1M input tokens, ~$30 per 1M output tokens
  - `gpt-3.5-turbo` - Fast and budget-friendly
    - Cost: ~$0.50 per 1M input tokens, ~$1.50 per 1M output tokens
- **Sign up**: [OpenAI Platform](https://platform.openai.com/signup)
- **Pricing**: [OpenAI Pricing](https://openai.com/api/pricing/)

##### **Anthropic Claude (Premium)**
- **Best for**: Excellent reasoning, complex code, long context
- **Recommended models for code**:
  - **`claude-4-opus`** - ⭐ Latest, highest quality, best for complex code (latest, premium)
    - Cost: Check current pricing (varies by plan)
    - Best for: Complex code, advanced debugging, agent workflows
    - Features: Enhanced coding and reasoning capabilities
  - **`claude-4-sonnet`** - ⭐ Latest, excellent for code, great balance (latest, recommended)
    - Cost: Check current pricing (varies by plan)
    - Best for: Complex code, debugging, refactoring, wide range of applications
    - Features: Improved coding capabilities, balanced performance
  - **`claude-3.5-sonnet`** - ⭐ Best for code generation, excellent reasoning
    - Cost: ~$3 per 1M input tokens, ~$15 per 1M output tokens
    - Best for: Complex code, debugging, refactoring
  - `claude-3-opus` - High quality, best for complex code
    - Cost: ~$15 per 1M input tokens, ~$75 per 1M output tokens
  - `claude-3-sonnet` - Good balance
    - Cost: ~$3 per 1M input tokens, ~$15 per 1M output tokens
  - `claude-3-haiku` - Fast and cost-effective
    - Cost: ~$0.25 per 1M input tokens, ~$1.25 per 1M output tokens
- **Sign up**: [Anthropic Console](https://console.anthropic.com/signup)
- **Pricing**: [Anthropic Pricing](https://www.anthropic.com/pricing)
- **Note**: Claude 4 models available to Pro, Max, Team, and Enterprise subscribers

##### **DeepSeek (Budget-Friendly)**
- **Best for**: Cost-effective code generation
- **Recommended models**:
  - **`deepseek-chat`** - General purpose, good for code (recommended)
    - Cost: ~$0.14 per 1M input tokens, ~$0.28 per 1M output tokens
  - `deepseek-coder` - Specialized for code generation
    - Cost: ~$0.14 per 1M input tokens, ~$0.28 per 1M output tokens
- **Sign up**: [DeepSeek Platform](https://platform.deepseek.com/signup)
- **Pricing**: [DeepSeek Pricing](https://www.deepseek.com/pricing)

#### Cost Comparison for Code Generation

For typical code generation tasks (100-500 tokens per request):

| Model | Cost per 1000 requests* | Quality | Speed |
|-------|------------------------|---------|-------|
| Ollama (local) | **$0.00** | Good | Fast |
| DeepSeek Chat | **~$0.10** | Good | Fast |
| GPT-4o-mini | **~$0.15** | Excellent | Fast |
| Claude 3.5 Sonnet | **~$0.50** | Excellent | Medium |
| GPT-5.2 | **~$0.75** | Best | Medium |
| GPT-4o | **~$1.00** | Best | Medium |
| Claude 4 Sonnet | **~$1.50** | Best | Medium |
| Claude 3 Opus | **~$2.50** | Best | Slower |
| Claude 4 Opus | **~$3.00+** | Best | Slower |

*Approximate costs for typical code generation queries. Actual costs vary based on query length and complexity.

#### Recommendations

- **For beginners or testing**: Start with **Ollama** (free) or **GPT-4o-mini** (low cost)
- **For production code**: Use **Claude 4 Sonnet**, **GPT-5.2**, or **Claude 3.5 Sonnet** (latest and best quality)
- **For complex/advanced code**: Use **Claude 4 Opus** or **GPT-5.2** (latest premium models)
- **For budget-conscious users**: **DeepSeek Chat** or **GPT-4o-mini** offer great value
- **For privacy-sensitive work**: Use **Ollama** (runs locally, no data sent to cloud)

#### Getting API Credits

1. **OpenAI**: Sign up at [platform.openai.com](https://platform.openai.com/signup) - $5 free credits for new users
2. **Anthropic**: Sign up at [console.anthropic.com](https://console.anthropic.com/signup) - Check current promotions
3. **DeepSeek**: Sign up at [platform.deepseek.com](https://platform.deepseek.com/signup) - Very affordable pricing

## Usage

### Quick Code Generation

Get instant code snippets and commands directly from your terminal - perfect for when you need something quick without leaving bash:

```bash
# Generate a Python script
nexus ask "create a Python function to parse JSON and extract email addresses"

# Get a bash one-liner
nexus ask "bash command to find all files modified in last 24 hours"

# Get a Docker command
nexus ask "docker command to run a container with port mapping and volume mount"

# Generate a complete script
nexus ask "create a shell script to backup MySQL database with timestamp"
```

The tool extracts and highlights all code blocks and commands, making it easy to copy and use them immediately.

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

### Error Debugging

Debug error messages instantly without leaving your terminal:

```bash
# Debug an error message
nexus debug "docker: Error response from daemon: port is already allocated"

# Or pipe directly from a command
docker run -p 80:80 nginx 2>&1 | nexus debug

# With verbose output
nexus debug --verbose "Permission denied: /var/log/app.log"
```

The debug command analyzes error messages and provides:
- What the error means
- Why it occurred
- Step-by-step solutions
- How to prevent it in the future

### Command Explanation

Understand complex commands with detailed breakdowns:

```bash
# Explain a command
nexus explain "docker run -d -p 8080:80 -v /data:/app/data --name myapp nginx:latest"

# Explain commands from a file
nexus explain --file deploy.sh

# Beginner-friendly explanation
nexus explain --learn "docker compose up"

# With verbose output
nexus explain --verbose "kubectl apply -f deployment.yaml"
```

The explain command breaks down:
- Each flag and argument
- What each part does
- Common use cases
- Alternative approaches
- Potential side effects

### Command Safety Check

Verify command safety before execution:

```bash
# Check if a command is safe
nexus check "rm -rf /tmp/*"
nexus check "curl http://example.com/script.sh | bash"

# Interactive mode with additional warning
nexus check --interactive "sudo chmod -R 777 /"
```

The check command provides:
- Safety assessment (Safe / Caution / Dangerous)
- Risk analysis
- Safer alternatives
- Best practices

### Script Generation

Generate production-ready scripts with best practices:

```bash
# Generate a bash script
nexus script "backup MySQL database with compression and email notification"

# Generate in specific language
nexus script --language python "deploy application to production"

# Save to file
nexus script --output deploy.sh "deploy script with error handling"

# With verbose output
nexus script --verbose "monitor system resources and send alerts"
```

Generated scripts include:
- Error handling (try/catch, exit codes)
- Logging functionality
- Input validation
- Configuration options
- Usage documentation
- Best practices for the language

### Workflow Automation

Automate repetitive system administration tasks with pre-built workflow templates:

```bash
# List available workflows
nexus workflow list

# Run a system health check
nexus workflow run system-health

# Run with verbose output
nexus workflow run security-audit --verbose

# Show workflow details
nexus workflow show docker-health

# Create a custom workflow from template
nexus workflow create my-check --from-template system-health
```

#### Available Workflow Templates

The following templates are automatically installed:

- **system-health** - Quick system health overview (disk, memory, CPU, services)
- **security-audit** - Security-focused checks (updates, failed logins, ports, firewall)
- **performance-check** - System performance metrics (top processes, I/O, network stats)
- **docker-health** - Docker and container status checks
- **network-diagnostics** - Network connectivity and configuration checks

#### Creating Custom Workflows

Workflows are YAML files that define a sequence of commands to execute. You can:

1. **Create from template**: Copy and customize an existing template
   ```bash
   nexus workflow create my-workflow --from-template system-health
   ```

2. **Create from scratch**: Create an empty workflow and edit it
   ```bash
   nexus workflow create my-workflow
   ```

3. **Edit workflows**: Workflows are stored in `~/.config/nexus/workflows/user/`

#### Workflow Features

- **Sequential execution**: Commands run in order
- **Error handling**: Continue on error or stop execution
- **Output capture**: Capture and display command output
- **Variable substitution**: Use `${VARIABLE}` in commands
- **Conditional execution**: Run alternatives if commands fail
- **Timeout protection**: Prevent commands from hanging
- **Verbose mode**: See step-by-step progress

Workflows are perfect for:
- Daily system health checks
- Security audits
- Performance monitoring
- Docker container management
- Network diagnostics
- Custom automation tasks

## Commands Reference

| Command | Description |
|---------|-------------|
| `nexus ask <question>` | Ask a question (quotes optional, checks cache first) |
| `nexus ask --verbose <question>` | Get verbose answer with full details |
| `nexus debug <error>` | Debug an error message and get a solution (or pipe from stdin) |
| `nexus explain <command>` | Explain what a command does in detail |
| `nexus explain --file <file>` | Explain commands from a file |
| `nexus explain --learn <command>` | Explain like I'm a beginner |
| `nexus check <command>` | Check if a command is safe to run |
| `nexus check --interactive <command>` | Check with interactive warning |
| `nexus script <description>` | Generate a production-ready script |
| `nexus script --language <lang> <description>` | Generate script in specific language |
| `nexus script --output <file> <description>` | Save generated script to file |
| `nexus save <category> <command>` | Save a command with category |
| `nexus save --category <cat> <command>` | Save with category flag |
| `nexus list [--category <cat>]` | List saved commands (optionally filtered) |
| `nexus quick <keyword>` | Quick access to saved commands (no AI) |
| `nexus history [--limit N]` | View command history |
| `nexus delete <id>` | Delete a saved command by ID |
| `nexus config` | Show current configuration |
| `nexus config --set-provider <provider>` | Set default AI provider |
| `nexus workflow list` | List available workflows |
| `nexus workflow list --all` | Show all workflows including templates |
| `nexus workflow run <name>` | Run a workflow by name |
| `nexus workflow run <name> --verbose` | Run workflow with verbose output |
| `nexus workflow run <name> --var KEY=VALUE` | Run workflow with variables |
| `nexus workflow show <name>` | Show workflow details |
| `nexus workflow create <name>` | Create a new workflow |
| `nexus workflow create <name> --from-template <template>` | Create workflow from template |

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

### Quick Code Generation from Terminal

Perfect for developers who need instant code snippets without leaving their terminal. Simply ask for what you need:

- **Generate scripts**: Create complete bash, Python, or other scripts on the fly
- **Get commands**: Instantly retrieve Linux, Docker, or system administration commands
- **Code snippets**: Get ready-to-use code blocks with proper syntax highlighting
- **One-liners**: Quick bash one-liners for common tasks

All code is automatically extracted and highlighted, making it easy to copy and paste directly into your workflow. No need to switch to a browser or IDE - get your code right where you need it.

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

### Error Debugging

When you encounter an error in your terminal, you can instantly debug it without leaving your workflow. The `nexus debug` command:

- Analyzes error messages and provides specific solutions
- Explains why the error occurred
- Suggests fixes with step-by-step instructions
- Can accept input from stdin (pipe errors directly)
- Caches common errors for instant responses

This eliminates the need to copy-paste errors into search engines or Stack Overflow, keeping you in your terminal workflow.

### Command Explanation

The `nexus explain` command helps you understand complex commands by breaking them down into digestible parts:

- Detailed breakdown of each flag and argument
- Explanation of what each part does
- Common use cases and examples
- Alternative approaches
- Potential side effects to be aware of
- Beginner-friendly mode with `--learn` flag

Perfect for learning new tools, understanding existing scripts, or teaching others.

### Command Safety Check

Before running potentially dangerous commands, use `nexus check` to verify safety:

- Analyzes commands for dangerous operations
- Flags destructive operations (rm, chmod, etc.)
- Checks for suspicious patterns (piping to bash, etc.)
- Provides risk assessment (Safe / Caution / Dangerous)
- Suggests safer alternatives
- Interactive mode for additional warnings

Helps prevent accidents and teaches best practices for command-line safety.

### Script Generation

Generate complete, production-ready scripts with `nexus script`:

- Full scripts with error handling, not just commands
- Includes logging, validation, and configuration
- Follows language-specific best practices
- Adds comments and documentation
- Supports multiple languages (bash, python, etc.)
- Can save directly to files

Saves hours of boilerplate code and ensures your scripts follow best practices from the start.

### Workflow Automation

Automate repetitive system administration tasks with pre-built workflow templates. Workflows allow you to:

- **Chain commands**: Execute multiple commands in sequence
- **Handle errors**: Configure how to handle failures (continue, stop, or use alternatives)
- **Capture output**: Collect and display results from each step
- **Use variables**: Substitute variables in commands for flexibility
- **Schedule tasks**: Perfect for regular system checks and monitoring

Workflow templates are automatically installed and ready to use. You can also create custom workflows for your specific needs.

### YouTube Transcription

Transcribe YouTube videos to text using local AI (Whisper) for privacy-first video analysis. Perfect for:
- Creating searchable transcripts of technical videos
- Analyzing tutorial content with AI
- Extracting information from conference talks
- Documenting video content

```bash
# Transcribe a YouTube video (default: base model)
nexus transcribe url "https://www.youtube.com/watch?v=VIDEO_ID"

# Use a specific Whisper model size
nexus transcribe url VIDEO_URL --model-size small

# Save to custom directory
nexus transcribe url VIDEO_URL --output-dir ~/my-transcriptions

# List all transcriptions
nexus transcribe list

# List with detailed information
nexus transcribe list --verbose
```

#### Whisper Model Sizes

Choose the right model based on your hardware and accuracy needs:

| Model | RAM Required | Speed | Accuracy | Use Case |
|-------|-------------|-------|----------|----------|
| `tiny` | ~1 GB | Fastest | Basic | Quick transcriptions, testing |
| `base` | ~1 GB | Fast | Good | **Default**, best balance |
| `small` | ~2 GB | Medium | Better | Higher quality transcriptions |
| `medium` | ~5 GB | Slower | High | Professional use |
| `large` | ~10 GB | Slowest | Best | Maximum accuracy needed |

#### Requirements

Before using transcription, install ffmpeg:

```bash
sudo apt update
sudo apt install -y ffmpeg
```

#### Output Format

Transcriptions are saved as text files with metadata headers:
- Location: `./transcriptions/` (configurable in config.yaml)
- Filename: `{video_id}_{timestamp}.txt`
- Contains: Video title, uploader, duration, and full transcript

#### Configuration

Add to `~/.config/nexus/config.yaml`:

```yaml
transcription:
  output_dir: ./transcriptions  # Where to save transcriptions
  default_model_size: base  # Default Whisper model
```

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
│   ├── rate_limiter.py # Rate limiting
│   └── workflows/     # Workflow system
│       ├── engine.py   # Workflow execution engine
│       └── templates/  # Built-in workflow templates
├── config/            # Configuration examples
├── scripts/           # Installation scripts
├── venv/              # Virtual environment
└── requirements.txt   # Dependencies
```

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

