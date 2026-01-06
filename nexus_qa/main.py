"""Main CLI entry point for Nexus CLI Assistant."""

import click
import sys
from nexus_qa.config import load_config, get_config_path
from nexus_qa.storage import Storage
from nexus_qa.cache import Cache
from nexus_qa.rate_limiter import RateLimiter
from nexus_qa.ai_client import create_client
from nexus_qa.formatter import Formatter


@click.group()
@click.version_option(version="0.2.0")
def cli():
    """Nexus CLI Assistant - Quick AI-powered answers for Linux/Docker/Ollama questions."""
    pass


@cli.command()
@click.argument("question", nargs=-1, required=True)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def ask(question: tuple, verbose: bool):
    """Ask a question and get an AI-powered answer.
    
    You can provide the question with or without quotes.
    Example: nexus ask how to check docker status
    Example: nexus ask "how to check docker status"
    """
    # Join multiple arguments into a single question string
    question_str = " ".join(question)
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
        cached_response = cache.get(question_str, provider_name)
        from_cache = cached_response is not None
        
        if cached_response:
            response = cached_response
        else:
            # Ask AI
            response = client.ask(question_str, verbose=verbose)
            
            # Save to history
            storage.save_history(question_str, response, provider_name)
        
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
@click.argument("provider", required=False)
@click.option("--set-provider", "-s", "set_provider", help="Set default AI provider (ollama, openai, anthropic, deepseek)")
def config(provider: str, set_provider: str):
    """Show or set current configuration.
    
    Show config: nexus config
    Set provider: nexus config --set-provider ollama
    """
    formatter = Formatter()
    config_path = get_config_path()
    
    # If setting provider
    if set_provider:
        from nexus_qa.config import set_default_provider
        try:
            set_default_provider(set_provider)
            formatter.format_success(f"Default provider set to: {set_provider}")
            formatter.format_info(f"Configuration updated in: {config_path}")
        except Exception as e:
            formatter.format_error(str(e))
        return
    
    # Show current configuration
    config = load_config()
    
    formatter.format_info(f"Configuration file: {config_path}")
    formatter.format_info(f"AI Provider: [bold cyan]{config.ai_provider}[/bold cyan] (default)")
    formatter.format_info(f"Default Model: {config.default_model}")
    formatter.format_info(f"Output Mode: {config.output_mode}")
    formatter.format_info(f"Rate Limiting: {'Enabled' if config.rate_limiting.enabled else 'Disabled'}")
    formatter.format_info(f"Cache: {'Enabled' if config.cache.enabled else 'Disabled'}")
    
    if config.providers:
        formatter.format_info("\nConfigured Providers:")
        for name, provider_config in config.providers.items():
            marker = " ← current" if name == config.ai_provider else ""
            formatter.format_info(f"  - {name}: {provider_config.model}{marker}")
    
    formatter.format_info("\nTo change default provider: nexus config --set-provider <provider>")


@cli.command()
@click.argument("error_message", nargs=-1, required=False)
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def debug(error_message: tuple, verbose: bool):
    """Debug an error message and get a solution.
    
    You can provide the error message as an argument or pipe it from stdin.
    Example: nexus debug "docker: Error response from daemon: port is already allocated"
    Example: docker run -p 80:80 nginx 2>&1 | nexus debug
    """
    try:
        # Get error message from argument or stdin
        if error_message:
            error_str = " ".join(error_message)
        else:
            # Read from stdin if available
            if not sys.stdin.isatty():
                error_str = sys.stdin.read().strip()
            else:
                formatter = Formatter()
                formatter.format_error("No error message provided. Provide as argument or pipe from stdin.")
                return
        
        if not error_str:
            formatter = Formatter()
            formatter.format_error("Error message is empty.")
            return
        
        # Create prompt for error debugging
        debug_prompt = f"""I encountered the following error. Please analyze it and provide:
1. What the error means
2. Why it occurred
3. Step-by-step solution to fix it
4. How to prevent it in the future

Error message:
{error_str}

Provide a clear, actionable solution with commands if applicable."""
        
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
        
        # Check cache first (use error message as key)
        cache_key = f"debug:{error_str}"
        cached_response = cache.get(cache_key, provider_name)
        from_cache = cached_response is not None
        
        if cached_response:
            response = cached_response
        else:
            # Ask AI
            response = client.ask(debug_prompt, verbose=verbose)
            
            # Save to cache and history
            cache.set(cache_key, response, provider_name)
            storage.save_history(f"debug: {error_str[:100]}", response, provider_name)
        
        # Format and display
        formatter.format_response(response, from_cache=from_cache)
        
    except Exception as e:
        formatter = Formatter()
        formatter.format_error(str(e))


@cli.command()
@click.argument("command", nargs=-1, required=False)
@click.option("--file", "-f", "file_path", help="Explain commands from a file")
@click.option("--learn", "-l", is_flag=True, help="Explain like I'm a beginner")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def explain(command: tuple, file_path: str, learn: bool, verbose: bool):
    """Explain what a command does in detail.
    
    Example: nexus explain "docker run -d -p 8080:80 -v /data:/app/data --name myapp nginx:latest"
    Example: nexus explain --file deploy.sh
    Example: nexus explain --learn "docker compose up"
    """
    try:
        if file_path:
            # Read from file
            try:
                with open(file_path, 'r') as f:
                    command_str = f.read()
            except FileNotFoundError:
                formatter = Formatter()
                formatter.format_error(f"File not found: {file_path}")
                return
            except Exception as e:
                formatter = Formatter()
                formatter.format_error(f"Error reading file: {str(e)}")
                return
        else:
            if not command:
                formatter = Formatter()
                formatter.format_error("Command is required. Provide as argument or use --file option.")
                return
            command_str = " ".join(command)
        
        if not command_str.strip():
            formatter = Formatter()
            formatter.format_error("Command is empty.")
            return
        
        # Create prompt for command explanation
        learn_mode = "Explain this like I'm a beginner. " if learn else ""
        explain_prompt = f"""{learn_mode}Please explain the following command(s) in detail:

{command_str}

Provide:
1. What the command does overall
2. Breakdown of each flag/argument and what it does
3. Common use cases
4. Alternative approaches (if applicable)
5. Potential side effects or things to be aware of

Format the explanation clearly with sections for each part."""
        
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
        cache_key = f"explain:{command_str}"
        if learn:
            cache_key = f"explain:learn:{command_str}"
        cached_response = cache.get(cache_key, provider_name)
        from_cache = cached_response is not None
        
        if cached_response:
            response = cached_response
        else:
            # Ask AI
            response = client.ask(explain_prompt, verbose=verbose)
            
            # Save to cache and history
            cache.set(cache_key, response, provider_name)
            storage.save_history(f"explain: {command_str[:100]}", response, provider_name)
        
        # Format and display
        formatter.format_response(response, from_cache=from_cache)
        
    except Exception as e:
        formatter = Formatter()
        formatter.format_error(str(e))


@cli.command()
@click.argument("command", nargs=-1, required=True)
@click.option("--interactive", "-i", is_flag=True, help="Show interactive warning before execution")
def check(command: tuple, interactive: bool):
    """Check if a command is safe to run.
    
    Analyzes the command for dangerous operations and provides safety warnings.
    Example: nexus check "rm -rf /tmp/*"
    Example: nexus check "curl http://example.com/script.sh | bash"
    """
    try:
        command_str = " ".join(command)
        
        if not command_str.strip():
            formatter = Formatter()
            formatter.format_error("Command is empty.")
            return
        
        # Create prompt for safety check
        safety_prompt = f"""Analyze the following command for safety and security:

{command_str}

Provide:
1. Safety assessment (Safe / Caution / Dangerous)
2. What the command does
3. Potential risks and why they're dangerous
4. Safer alternatives (if applicable)
5. Best practices for this type of operation

Be specific about destructive operations, security risks, and data loss potential."""
        
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
        
        formatter = Formatter(verbose=True)  # Always verbose for safety checks
        
        # Check cache first
        cache_key = f"check:{command_str}"
        cached_response = cache.get(cache_key, provider_name)
        from_cache = cached_response is not None
        
        if cached_response:
            response = cached_response
        else:
            # Ask AI
            response = client.ask(safety_prompt, verbose=True)
            
            # Save to cache and history
            cache.set(cache_key, response, provider_name)
            storage.save_history(f"check: {command_str[:100]}", response, provider_name)
        
        # Format and display
        formatter.format_response(response, from_cache=from_cache)
        
        # If interactive mode, show additional warning
        if interactive:
            formatter.format_info("\n⚠️  Review the analysis above before executing this command.")
        
    except Exception as e:
        formatter = Formatter()
        formatter.format_error(str(e))


@cli.command()
@click.argument("description", nargs=-1, required=True)
@click.option("--language", "-l", default="bash", help="Script language (bash, python, etc.)")
@click.option("--output", "-o", "output_file", help="Save script to file")
@click.option("--verbose", "-v", is_flag=True, help="Show verbose output")
def script(description: tuple, language: str, output_file: str, verbose: bool):
    """Generate a complete, production-ready script.
    
    Example: nexus script "backup MySQL database with compression and email notification"
    Example: nexus script "deploy application" --language python --output deploy.py
    """
    try:
        description_str = " ".join(description)
        
        if not description_str.strip():
            formatter = Formatter()
            formatter.format_error("Description is empty.")
            return
        
        # Create prompt for script generation
        script_prompt = f"""Generate a complete, production-ready {language} script based on this description:

{description_str}

The script must include:
1. Proper error handling (try/catch, exit codes, etc.)
2. Logging functionality
3. Input validation
4. Configuration options (use environment variables or config file)
5. Usage documentation/comments
6. Best practices for the language
7. Proper shebang line if applicable

Provide the complete script with all necessary components. Include comments explaining key parts."""
        
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
        cache_key = f"script:{language}:{description_str}"
        cached_response = cache.get(cache_key, provider_name)
        from_cache = cached_response is not None
        
        if cached_response:
            response = cached_response
        else:
            # Ask AI
            response = client.ask(script_prompt, verbose=verbose)
            
            # Save to cache and history
            cache.set(cache_key, response, provider_name)
            storage.save_history(f"script: {description_str[:100]}", response, provider_name)
        
        # Format and display
        formatter.format_response(response, from_cache=from_cache)
        
        # Save to file if requested
        if output_file:
            try:
                # Extract script from response (look for code blocks)
                script_content = response
                if "```" in response:
                    # Extract first code block
                    parts = response.split("```")
                    if len(parts) >= 3:
                        script_content = parts[1].split("\n", 1)[1] if "\n" in parts[1] else parts[1]
                
                with open(output_file, 'w') as f:
                    f.write(script_content)
                formatter.format_success(f"Script saved to: {output_file}")
            except Exception as e:
                formatter.format_error(f"Error saving script to file: {str(e)}")
        
    except Exception as e:
        formatter = Formatter()
        formatter.format_error(str(e))


if __name__ == "__main__":
    cli()

