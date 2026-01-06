"""Output formatting for Nexus CLI Assistant."""

from typing import List  # type: ignore
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


class Formatter:
    """Formatter for brief and verbose output modes."""
    
    def __init__(self, verbose: bool = False):
        """Initialize formatter."""
        self.console = Console()
        self.verbose = verbose
    
    def format_response(self, response: str, from_cache: bool = False):
        """Format AI response based on mode."""
        if from_cache:
            self.console.print("[dim]📦 Cached response[/dim]\n")
        
        if self.verbose:
            # Verbose mode: full markdown rendering
            self.console.print(Markdown(response))
        else:
            # Brief mode: extract key commands and simplify
            formatted = self._extract_brief(response)
            self.console.print(formatted)
    
    def _extract_brief(self, response: str) -> str:
        """Extract brief summary from response."""
        lines = response.split('\n')
        brief_lines = []
        in_code_block = False
        
        for line in lines:
            # Skip markdown headers in brief mode
            if line.strip().startswith('#'):
                # Convert headers to bold text
                header_text = line.lstrip('#').strip()
                if header_text:
                    brief_lines.append(f"**{header_text}**")
                continue
            
            # Keep code blocks
            if line.strip().startswith('```'):
                in_code_block = not in_code_block
                brief_lines.append(line)
                continue
            
            if in_code_block:
                brief_lines.append(line)
                continue
            
            # Keep bullet points and numbered lists
            if line.strip().startswith(('-', '*', '1.', '2.', '3.', '4.', '5.')):
                brief_lines.append(line)
                continue
            
            # Keep lines with commands (usually contain $, sudo, or common commands)
            if any(keyword in line for keyword in ['$', 'sudo', 'apt', 'docker', 'ufw', 'systemctl', 'git']):
                brief_lines.append(line)
                continue
        
        result = '\n'.join(brief_lines)
        
        # If we didn't extract much, show first few sentences
        if len(brief_lines) < 3:
            sentences = response.split('.')[:3]
            result = '. '.join(sentences) + '.'
        
        return result
    
    def format_command_list(self, commands: List, category: str = None):
        """Format list of saved commands."""
        if not commands:
            self.console.print("[yellow]No commands found.[/yellow]")
            return
        
        table = Table(title=f"Saved Commands{f' - {category}' if category else ''}")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Command", style="green")
        table.add_column("Category", style="blue")
        table.add_column("Description", style="dim")
        table.add_column("Created", style="dim")
        
        for cmd in commands:
            created = cmd.created_at.strftime("%Y-%m-%d") if cmd.created_at else "N/A"
            table.add_row(
                str(cmd.id),
                cmd.command,
                cmd.category,
                cmd.description or "",
                created,
            )
        
        self.console.print(table)
    
    def format_history(self, history: List, limit: int = 20):
        """Format command history."""
        if not history:
            self.console.print("[yellow]No history found.[/yellow]")
            return
        
        table = Table(title=f"Command History (last {limit})")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Query", style="green")
        table.add_column("Provider", style="blue")
        table.add_column("Created", style="dim")
        
        for entry in history:
            created = entry.created_at.strftime("%Y-%m-%d %H:%M") if entry.created_at else "N/A"
            table.add_row(
                str(entry.id),
                entry.query[:50] + "..." if len(entry.query) > 50 else entry.query,
                entry.provider or "N/A",
                created,
            )
        
        self.console.print(table)
    
    def format_error(self, error: str):
        """Format error message."""
        self.console.print(f"[red]Error:[/red] {error}")
    
    def format_success(self, message: str):
        """Format success message."""
        self.console.print(f"[green]✓[/green] {message}")
    
    def format_info(self, message: str):
        """Format info message."""
        self.console.print(f"[blue]ℹ[/blue] {message}")

