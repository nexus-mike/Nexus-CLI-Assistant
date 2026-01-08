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
mkdir -p "$CONFIG_DIR/workflows/templates"
mkdir -p "$CONFIG_DIR/workflows/user"

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

# Copy workflow templates if they don't exist
echo "📋 Installing workflow templates..."
TEMPLATES_SOURCE="$PROJECT_DIR/nexus_qa/workflows/templates"
TEMPLATES_DEST="$CONFIG_DIR/workflows/templates"

if [ -d "$TEMPLATES_SOURCE" ]; then
    # Copy templates, but don't overwrite existing user customizations
    template_count=0
    for template in "$TEMPLATES_SOURCE"/*.yaml; do
        if [ -f "$template" ]; then
            template_name=$(basename "$template")
            if [ ! -f "$TEMPLATES_DEST/$template_name" ]; then
                cp "$template" "$TEMPLATES_DEST/"
                template_count=$((template_count + 1))
            fi
        fi
    done
    
    # Copy README if it exists
    if [ -f "$TEMPLATES_SOURCE/README.md" ]; then
        cp "$TEMPLATES_SOURCE/README.md" "$TEMPLATES_DEST/" 2>/dev/null || true
    fi
    
    if [ $template_count -gt 0 ]; then
        echo "✓ Installed $template_count workflow template(s)"
    else
        echo "✓ Workflow templates already installed"
    fi
else
    echo "⚠ Workflow templates directory not found (this is normal for first-time setup)"
fi

# Function to detect user's shell
detect_shell() {
    if [ -n "$ZSH_VERSION" ]; then
        echo "zsh"
    elif [ -n "$BASH_VERSION" ]; then
        echo "bash"
    elif [ -n "$FISH_VERSION" ]; then
        echo "fish"
    else
        # Fallback: check $SHELL environment variable
        basename "$SHELL" 2>/dev/null || echo "bash"
    fi
}

# Function to get shell config file path
get_shell_config() {
    local shell_type="$1"
    case "$shell_type" in
        zsh)
            echo "$HOME/.zshrc"
            ;;
        bash)
            if [ -f "$HOME/.bash_profile" ]; then
                echo "$HOME/.bash_profile"
            else
                echo "$HOME/.bashrc"
            fi
            ;;
        fish)
            echo "$HOME/.config/fish/config.fish"
            ;;
        *)
            echo "$HOME/.bashrc"
            ;;
    esac
}

# Function to check if nexus alias/config already exists
nexus_alias_exists() {
    local config_file="$1"
    if [ ! -f "$config_file" ]; then
        return 1
    fi
    grep -q "nexus.*venv.*activate" "$config_file" 2>/dev/null || \
    grep -q "alias nexus=" "$config_file" 2>/dev/null || \
    grep -q "# Nexus CLI Assistant" "$config_file" 2>/dev/null
}

# Function to add nexus alias to shell config
add_nexus_alias() {
    local config_file="$1"
    local shell_type="$2"
    
    # Create config file if it doesn't exist
    mkdir -p "$(dirname "$config_file")"
    touch "$config_file"
    
    # Check if already exists
    if nexus_alias_exists "$config_file"; then
        echo "⚠ Nexus alias already exists in $config_file"
        echo "   Skipping alias setup. If you need to update it, edit the file manually."
        return 1
    fi
    
    # Add alias based on shell type
    {
        echo ""
        echo "# Nexus CLI Assistant - Auto-configured by installer"
        if [ "$shell_type" = "fish" ]; then
            echo "alias nexus='source $VENV_DIR/bin/activate.fish; and nexus'"
        else
            echo "alias nexus='source $VENV_DIR/bin/activate && nexus'"
        fi
    } >> "$config_file"
    
    return 0
}

# Ask user about automatic setup
echo ""
echo "🔧 Command Setup"
echo "Would you like to configure the 'nexus' command to work without manually activating the virtual environment?"
echo ""
echo "Options:"
echo "  1) User-specific (recommended) - Adds alias to your shell config file"
echo "  2) Skip - You'll need to activate venv manually or add alias yourself"
echo ""
read -p "Choose option [1/2] (default: 1): " setup_choice
setup_choice=${setup_choice:-1}

if [ "$setup_choice" = "1" ]; then
    SHELL_TYPE=$(detect_shell)
    SHELL_CONFIG=$(get_shell_config "$SHELL_TYPE")
    
    echo ""
    echo "📝 Detected shell: $SHELL_TYPE"
    echo "📝 Config file: $SHELL_CONFIG"
    
    if add_nexus_alias "$SHELL_CONFIG" "$SHELL_TYPE"; then
        echo "✓ Added nexus alias to $SHELL_CONFIG"
        echo ""
        echo "⚠️  IMPORTANT: To use the 'nexus' command in this session, run:"
        echo "   source $SHELL_CONFIG"
        echo ""
        echo "   Or open a new terminal window for the changes to take effect."
    fi
else
    echo "⏭️  Skipping automatic setup."
    echo ""
    echo "To set up manually later, add to your shell config:"
    echo "  alias nexus='source $VENV_DIR/bin/activate && nexus'"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "Configuration file: $CONFIG_FILE"
echo ""

