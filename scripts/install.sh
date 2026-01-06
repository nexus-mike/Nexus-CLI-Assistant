#!/bin/bash

# Nexus CLI Assistant Installation Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "🚀 Installing Nexus CLI Assistant..."
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create virtual environment
VENV_DIR="$PROJECT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "⚠ Virtual environment already exists. Removing old one..."
    rm -rf "$VENV_DIR"
fi

echo "📦 Creating virtual environment..."
python3 -m venv "$VENV_DIR"

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "⬆ Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r "$PROJECT_DIR/requirements.txt" --quiet

# Install package in editable mode
echo "📦 Installing Nexus CLI Assistant..."
pip install -e "$PROJECT_DIR" --quiet

# Create config directory
CONFIG_DIR="$HOME/.config/nexus"
mkdir -p "$CONFIG_DIR"
mkdir -p "$CONFIG_DIR/data"

# Copy example config if it doesn't exist
CONFIG_FILE="$CONFIG_DIR/config.yaml"
if [ ! -f "$CONFIG_FILE" ]; then
    echo "📝 Creating default configuration..."
    if [ -f "$PROJECT_DIR/config/config.yaml.example" ]; then
        cp "$PROJECT_DIR/config/config.yaml.example" "$CONFIG_FILE"
        echo "✓ Configuration file created at $CONFIG_FILE"
    else
        echo "⚠ Example config not found, creating minimal config..."
        cat > "$CONFIG_FILE" << EOF
ai_provider: ollama
default_model: llama3.2
output_mode: brief

rate_limiting:
  enabled: true
  requests_per_minute: 30
  requests_per_hour: 500

cache:
  enabled: true
  ttl_seconds: 3600
  max_entries: 1000

providers:
  ollama:
    base_url: http://localhost:11434
    model: llama3.2
EOF
    fi
else
    echo "✓ Configuration file already exists at $CONFIG_FILE"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "To use Nexus CLI Assistant:"
echo "  1. Activate the virtual environment: source $VENV_DIR/bin/activate"
echo "  2. Run: nexus ask 'your question here'"
echo ""
echo "Or add to your ~/.bashrc or ~/.zshrc:"
echo "  alias nexus='source $VENV_DIR/bin/activate && nexus'"
echo ""
echo "Configuration file: $CONFIG_FILE"
echo ""

