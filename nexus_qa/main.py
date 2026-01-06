"""Main CLI entry point for Nexus CLI Assistant."""

import click
from nexus_qa.config import load_config, get_config_path
from nexus_qa.storage import Storage
from nexus_qa.cache import Cache
from nexus_qa.rate_limiter import RateLimiter
from nexus_qa.ai_client import create_client
from nexus_qa.formatter import Formatter


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Nexus CLI Assistant - Quick AI-powered answers for Linux/Docker/Ollama questions."""
    pass


@cli.command()
@click.argument("question", required=True)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def ask(question: str, verbose: bool):
    """Ask a question and get an AI-powered answer."""
    try:
        config = load_config()
        storage = Storage()
        cache = Cache(storage, config.cache)
        rate_limiter = RateLimiter(config.rate_limiting)
        
        # Get provider config
        provider_name = config.ai_provider
        if provider_name not in config.providers:
            click.echo(f"Error: Provider '{provider_name}' not configured.", err=True)
            return
        
        provider_config = config.providers[provider_name]
        client = create_client(provider_name, provider_config, rate_limiter, cache)
        
        formatter = Formatter(verbose=verbose)
        
        # Check cache first
        cached_response = cache.get(question, provider_name)
        from_cache = cached_response is not None
        
        if cached_response:
            response = cached_response
        else:
            # Ask AI
            response = client.ask(question, verbose=verbose)
            
            # Save to history
            storage.save_history(question, response, provider_name)
        
        # Format and display
        formatter.format_response(response, from_cache=from_cache)
        
    except Exception as e:
        formatter = Formatter()
        formatter.format_error(str(e))


@cli.command()
@click.argument("category", required=False)
@click.option("--category", "-c", "category_flag", help="Filter by category")
@click.option("--all", "-a", "show_all", is_flag=True, help="Show all commands")
def list(category: str, category_flag: str, show_all: bool):
    """List saved commands, optionally filtered by category."""
    storage = Storage()
    formatter = Formatter()
    
    # Determine category
    cat = category or category_flag
    
    if show_all or not cat:
        commands = storage.get_commands()
    else:
        commands = storage.get_commands(category=cat)
    
    formatter.format_command_list(commands, category=cat)


@cli.command()
@click.argument("category", required=False)
@click.argument("command", required=False)
@click.option("--category", "-c", "category_flag", help="Category for the command")
@click.option("--description", "-d", help="Description for the command")
def save(category: str, command: str, category_flag: str, description: str):
    """Save a command to the database.
    
    Usage:
        nexus save <category> <command>
        nexus save --category <category> <command>
    """
    storage = Storage()
    formatter = Formatter()
    
    # Determine category and command
    # If category is provided as first arg and command as second
    if category and command and not category_flag:
        cat = category
        cmd = command
    elif category_flag and command:
        cat = category_flag
        cmd = command
    elif category and not command:
        # Only category provided, need command
        formatter.format_error("Command is required. Usage: nexus save <category> <command>")
        return
    else:
        formatter.format_error("Category and command are required. Usage: nexus save <category> <command>")
        return
    
    command_id = storage.save_command(cmd, cat, description)
    formatter.format_success(f"Command saved with ID {command_id}")


@cli.command()
@click.argument("keyword", required=True)
def quick(keyword: str):
    """Quick access to saved commands by keyword (no AI processing)."""
    storage = Storage()
    formatter = Formatter()
    
    commands = storage.search_commands(keyword)
    
    if not commands:
        formatter.format_info(f"No commands found matching '{keyword}'")
        return
    
    formatter.format_command_list(commands)


@cli.command()
@click.option("--limit", "-l", default=20, help="Number of entries to show")
def history(limit: int):
    """View command history."""
    storage = Storage()
    formatter = Formatter()
    
    history_entries = storage.get_history(limit=limit)
    formatter.format_history(history_entries, limit=limit)


@cli.command()
@click.argument("command_id", type=int, required=True)
def delete(command_id: int):
    """Delete a saved command by ID."""
    storage = Storage()
    formatter = Formatter()
    
    deleted = storage.delete_command(command_id)
    
    if deleted:
        formatter.format_success(f"Command {command_id} deleted")
    else:
        formatter.format_error(f"Command {command_id} not found")


@cli.command()
def config():
    """Show current configuration."""
    config = load_config()
    formatter = Formatter()
    
    config_path = get_config_path()
    
    formatter.format_info(f"Configuration file: {config_path}")
    formatter.format_info(f"AI Provider: {config.ai_provider}")
    formatter.format_info(f"Default Model: {config.default_model}")
    formatter.format_info(f"Output Mode: {config.output_mode}")
    formatter.format_info(f"Rate Limiting: {'Enabled' if config.rate_limiting.enabled else 'Disabled'}")
    formatter.format_info(f"Cache: {'Enabled' if config.cache.enabled else 'Disabled'}")
    
    if config.providers:
        formatter.format_info("\nConfigured Providers:")
        for name, provider_config in config.providers.items():
            formatter.format_info(f"  - {name}: {provider_config.model}")


if __name__ == "__main__":
    cli()

