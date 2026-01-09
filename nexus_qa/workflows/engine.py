"""Workflow execution engine for Nexus CLI Assistant."""

import subprocess
import shlex
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime
import os
import sys

from nexus_qa.models import Workflow, WorkflowStep, WorkflowExecution


class WorkflowEngine:
    """Engine for loading and executing workflows."""
    
    def __init__(self):
        """Initialize the workflow engine."""
        self.config_dir = Path.home() / ".config" / "nexus"
        self.templates_dir = self.config_dir / "workflows" / "templates"
        self.user_dir = self.config_dir / "workflows" / "user"
        
        # Package templates directory (for built-in templates)
        # This works both in development and when installed as a package
        package_dir = Path(__file__).parent.parent
        self.package_templates_dir = package_dir / "workflows" / "templates"
        
        # Ensure directories exist
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.user_dir.mkdir(parents=True, exist_ok=True)
    
    def get_template_paths(self) -> List[Path]:
        """Get paths to all available workflow templates."""
        templates = []
        
        # Package templates (built-in)
        if self.package_templates_dir.exists():
            templates.extend(self.package_templates_dir.glob("*.yaml"))
        
        # User directory templates
        if self.user_dir.exists():
            templates.extend(self.user_dir.glob("*.yaml"))
        
        # Config directory templates (installed)
        if self.templates_dir.exists():
            templates.extend(self.templates_dir.glob("*.yaml"))
        
        return sorted(set(templates))
    
    def load_workflow(self, name: str) -> Optional[Workflow]:
        """Load a workflow by name from templates or user directory."""
        # Try user directory first
        user_path = self.user_dir / f"{name}.yaml"
        if user_path.exists():
            return self._load_from_file(user_path)
        
        # Try templates directory
        template_path = self.templates_dir / f"{name}.yaml"
        if template_path.exists():
            return self._load_from_file(template_path)
        
        # Try package templates
        package_path = self.package_templates_dir / f"{name}.yaml"
        if package_path.exists():
            return self._load_from_file(package_path)
        
        return None
    
    def _load_from_file(self, file_path: Path) -> Optional[Workflow]:
        """Load workflow from a YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data:
                return None
            
            # Parse steps
            steps = []
            for step_data in data.get('steps', []):
                steps.append(WorkflowStep(**step_data))
            
            # Create workflow
            workflow = Workflow(
                name=data.get('name', file_path.stem),
                version=data.get('version', '1.0.0'),
                description=data.get('description', ''),
                author=data.get('author'),
                category=data.get('category', 'general'),
                tags=data.get('tags', []),
                steps=steps,
                output_format=data.get('output_format', 'summary'),
                estimated_duration=data.get('estimated_duration'),
                variables=data.get('variables', {})
            )
            
            return workflow
        except Exception as e:
            print(f"Error loading workflow from {file_path}: {e}", file=sys.stderr)
            return None
    
    def list_workflows(self) -> Dict[str, Dict[str, Any]]:
        """List all available workflows."""
        workflows = {}
        
        # Get all template paths
        template_paths = self.get_template_paths()
        
        for path in template_paths:
            workflow = self._load_from_file(path)
            if workflow:
                source = "user" if path.parent == self.user_dir else "template"
                workflows[workflow.name] = {
                    'workflow': workflow,
                    'source': source,
                    'path': str(path)
                }
        
        return workflows
    
    def execute_step(self, step: WorkflowStep, variables: Dict[str, str] = None) -> Dict[str, Any]:
        """Execute a single workflow step."""
        if variables is None:
            variables = {}

        # Substitute variables in command
        command = step.command
        for key, value in variables.items():
            replacement = str(value)
            if step.shell:
                replacement = shlex.quote(replacement)
            command = command.replace(f"${{{key}}}", replacement)
        
        result = {
            'step_name': step.name,
            'command': command,
            'success': False,
            'output': '',
            'error': None,
            'exit_code': None,
            'duration': 0
        }
        
        start_time = datetime.now()
        
        try:
            # Check if root is required
            if step.requires_root and os.geteuid() != 0:
                if step.skip_if_no_permission:
                    result['output'] = "Skipped: requires root privileges"
                    result['success'] = True
                    return result
                else:
                    result['error'] = "This step requires root privileges"
                    return result
            
            # Execute command
            timeout = step.timeout or 30
            if step.shell:
                argv = command
                shell = True
            else:
                try:
                    argv = shlex.split(command)
                except ValueError as exc:
                    result['error'] = f"Failed to parse command: {exc}"
                    return result
                if not argv:
                    result['error'] = "Command is empty after parsing"
                    return result
                shell = False
            process = subprocess.run(
                argv,
                shell=shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            result['exit_code'] = process.returncode
            result['output'] = process.stdout
            if process.stderr:
                result['error'] = process.stderr
            
            # Check conditions
            if step.fail_if_exit_code_nonzero and process.returncode != 0:
                result['success'] = False
            elif step.fail_if_empty and not process.stdout.strip():
                result['success'] = False
                result['error'] = "Command produced no output"
            elif step.fail_if_output_contains and step.fail_if_output_contains in process.stdout:
                result['success'] = False
                result['error'] = f"Output contains forbidden string: {step.fail_if_output_contains}"
            elif process.returncode == 0:
                result['success'] = True
            else:
                result['success'] = step.continue_on_error
            
        except subprocess.TimeoutExpired:
            result['error'] = f"Command timed out after {timeout} seconds"
            result['success'] = step.continue_on_error
        except Exception as e:
            result['error'] = str(e)
            result['success'] = step.continue_on_error
        
        end_time = datetime.now()
        result['duration'] = (end_time - start_time).total_seconds()
        
        return result
    
    def execute_workflow(self, workflow: Workflow, variables: Dict[str, str] = None, 
                        verbose: bool = False) -> WorkflowExecution:
        """Execute a complete workflow."""
        if variables is None:
            variables = {}
        
        # Merge workflow variables with provided variables
        all_variables = {**workflow.variables, **variables}
        
        execution = WorkflowExecution(
            workflow_name=workflow.name,
            started_at=datetime.now(),
            status='running',
            total_steps=len(workflow.steps),
            steps_completed=0
        )
        
        results = []
        output_lines = []
        
        if verbose:
            print(f"🚀 Executing workflow: {workflow.name}")
            print(f"📋 Description: {workflow.description}")
            print(f"📊 Steps: {len(workflow.steps)}")
            print()
        
        for i, step in enumerate(workflow.steps, 1):
            if verbose:
                print(f"[{i}/{len(workflow.steps)}] {step.name}...", end=' ', flush=True)
            
            step_result = self.execute_step(step, all_variables)
            results.append(step_result)
            execution.steps_completed = i
            
            # Format output
            if step_result['success']:
                status_icon = "✓"
                if verbose:
                    print(f"{status_icon} ({step_result['duration']:.2f}s)")
                
                if step.capture_output and step_result['output']:
                    output_lines.append(f"✓ {step.name}:")
                    output_lines.append(step_result['output'])
                    if step.warn_on_output and step_result['output'].strip():
                        output_lines.append("⚠ Warning: Output detected")
            else:
                status_icon = "✗"
                if verbose:
                    print(f"{status_icon} ({step_result['duration']:.2f}s)")
                
                output_lines.append(f"✗ {step.name}:")
                if step_result['error']:
                    output_lines.append(f"Error: {step_result['error']}")
                if step_result['output']:
                    output_lines.append(step_result['output'])
                
                # Check if we should continue
                if not step.continue_on_error:
                    execution.status = 'failed'
                    execution.error = f"Step '{step.name}' failed: {step_result.get('error', 'Unknown error')}"
                    break
                else:
                    # Try alternative command if available
                    if step.alternative:
                        if verbose:
                            print(f"  Trying alternative command...", end=' ', flush=True)
                        alt_step = WorkflowStep(
                            name=step.name + "_alt",
                            command=step.alternative,
                            description=step.description,
                            capture_output=step.capture_output,
                            continue_on_error=True,
                            timeout=step.timeout,
                            shell=step.shell
                        )
                        alt_result = self.execute_step(alt_step, all_variables)
                        if alt_result['success']:
                            if verbose:
                                print("✓")
                            output_lines.append(f"✓ {step.name} (alternative):")
                            output_lines.append(alt_result['output'])
                        else:
                            if verbose:
                                print("✗")
        
        execution.completed_at = datetime.now()
        
        if execution.status == 'running':
            execution.status = 'completed'
        
        execution.output = '\n'.join(output_lines)
        
        return execution
