"""Output formatting for Nexus CLI Assistant."""

from typing import List, Tuple  # type: ignore
from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax
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
            cache_indicator = Text("📦 Cached response", style="dim")
        else:
            cache_indicator = None
        
        if self.verbose:
            # Verbose mode: structured panel with full content
            formatted_content = self._format_structured(response)
            panel = Panel(
                formatted_content,
                title="[bold bright_cyan]💡 Answer[/bold bright_cyan]",
                border_style="bright_cyan",
                padding=(1, 2),
                title_align="left"
            )
            if cache_indicator:
                self.console.print(cache_indicator)
                self.console.print("")
            self.console.print(panel)
        else:
            # Brief mode: structured but condensed
            formatted_content = self._format_structured(response, brief=True)
            panel = Panel(
                formatted_content,
                title="[bold bright_cyan]💡 Answer[/bold bright_cyan]",
                border_style="bright_cyan",
                padding=(1, 2),
                title_align="left"
            )
            if cache_indicator:
                self.console.print(cache_indicator)
                self.console.print("")
            self.console.print(panel)
    
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
    
    def _format_structured(self, response: str, brief: bool = False) -> Group:
        """Format response into structured sections (Commands, Explanation)."""
        commands, explanation = self._parse_response(response, brief)
        
        parts = []
        
        # Commands section
        if commands:
            parts.append(Text("📋 Commands:", style="bold cyan"))
            parts.append(Text(""))
            
            # Combine all commands into one code block
            all_commands = '\n'.join(commands)
            # Detect language from first command or default to bash
            lang = 'bash'  # Default for CLI commands
            if any(keyword in all_commands.lower() for keyword in ['python', 'import', 'def ']):
                lang = 'python'
            elif any(keyword in all_commands.lower() for keyword in ['javascript', 'const ', 'function']):
                lang = 'javascript'
            
            syntax = Syntax(
                all_commands,
                lang,
                theme="monokai",
                line_numbers=False,
                word_wrap=True
            )
            parts.append(syntax)
            parts.append(Text(""))
        
        # Explanation section
        if explanation:
            parts.append(Text("💡 Explanation:", style="bold yellow"))
            parts.append(Text(""))
            # Format explanation with markdown for proper formatting
            parts.append(Markdown(explanation))
        
        return Group(*parts)
    
    def _parse_response(self, response: str, brief: bool = False) -> Tuple[List[str], str]:
        """Parse response into commands and explanation."""
        commands = []
        explanation_parts = []
        
        lines = response.split('\n')
        in_code_block = False
        current_code = []
        code_lang = 'bash'
        
        # Common command patterns
        command_patterns = ['docker ', 'sudo ', 'apt ', 'systemctl ', 'ufw ', 'git ', 
                          'npm ', 'pip ', 'python ', 'curl ', 'wget ', 'kubectl ',
                          'helm ', 'kubectl ', 'ssh ', 'scp ', 'rsync ', 'tar ', 
                          'gzip ', 'unzip ', 'chmod ', 'chown ', 'ls ', 'cd ', 'cat ',
                          'grep ', 'find ', 'ps ', 'kill ', 'top ', 'htop ']
        
        for line in lines:
            # Handle code blocks
            if '```' in line:
                if in_code_block:
                    # End of code block
                    if current_code:
                        code_text = '\n'.join(current_code).strip()
                        if code_text:
                            commands.append(code_text)
                    current_code = []
                    in_code_block = False
                else:
                    # Start of code block
                    in_code_block = True
                    code_lang = line.replace('```', '').strip() or 'bash'
                continue
            
            if in_code_block:
                current_code.append(line)
                continue
            
            stripped = line.strip()
            import re
            
            # Pattern 1: Extract commands from numbered/bulleted lists with backticks
            # e.g., "1. `docker ps` - description" or "1. `docker ps:`"
            list_match = re.match(r'^(\d+\.|\*|-)\s*(.+)', stripped)
            if list_match:
                content = list_match.group(2).strip()
                
                # Check if it contains a backtick-wrapped command
                backtick_match = re.search(r'`([^`]+)`', content)
                if backtick_match:
                    cmd = backtick_match.group(1).strip().rstrip(':')  # Remove trailing colon
                    # Check if it's a real command - check if cmd starts with any command pattern
                    # or contains a command pattern (for commands like "docker ps")
                    is_valid_cmd = False
                    for pattern in command_patterns:
                        pattern_base = pattern.rstrip()  # Remove trailing space
                        if cmd.startswith(pattern_base) or pattern_base in cmd:
                            is_valid_cmd = True
                            break
                    if is_valid_cmd:
                        if cmd not in commands:
                            commands.append(cmd)
                        # Keep the line in explanation
                        explanation_parts.append(line)
                        continue
                
                # Check if content starts with a command (even without backticks)
                # e.g., "1. docker ps: description"
                if ':' in content:
                    potential_cmd = content.split(':')[0].strip()
                    if any(pattern in potential_cmd for pattern in command_patterns):
                        if potential_cmd not in commands:
                            commands.append(potential_cmd)
                        explanation_parts.append(line)
                        continue
            
            # Pattern 2: Check if line starts with command pattern
            is_command = any(stripped.startswith(prefix) for prefix in command_patterns)
            
            # Pattern 3: Line starts with $ (shell prompt)
            if stripped.startswith('$'):
                cmd = stripped.lstrip('$ ').strip()
                if cmd:
                    commands.append(cmd)
                    continue
            
            # Pattern 4: Backtick-wrapped commands (inline code)
            if '`' in stripped:
                import re
                # Extract commands from backticks
                backtick_commands = re.findall(r'`([^`]+)`', stripped)
                for cmd in backtick_commands:
                    if any(pattern in cmd for pattern in command_patterns):
                        # Only add if it's a substantial command, not just a word
                        if len(cmd.split()) > 1 or cmd in ['docker', 'git', 'kubectl']:
                            if cmd not in commands:
                                commands.append(cmd)
            
            # Collect explanation text (but skip lines that are just commands)
            if stripped:
                # Skip if this line is just a command without context
                if is_command and not any(char in stripped for char in [':', '-', '—', '•']):
                    # Might be a standalone command, check if it's in a list context
                    continue
                
                explanation_parts.append(line)
        
        # If we found code blocks but no explanation, use the original response
        explanation = '\n'.join(explanation_parts).strip()
        if not explanation and not commands:
            # Fallback: use original response as explanation
            explanation = response
        
        # Clean up explanation - remove excessive empty lines
        if explanation:
            explanation_lines = explanation.split('\n')
            cleaned = []
            prev_empty = False
            for line in explanation_lines:
                if line.strip():
                    cleaned.append(line)
                    prev_empty = False
                elif not prev_empty:
                    cleaned.append(line)
                    prev_empty = True
            explanation = '\n'.join(cleaned).strip()
        
        # Remove duplicate commands
        commands = list(dict.fromkeys(commands))  # Preserves order
        
        return commands, explanation
    
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

