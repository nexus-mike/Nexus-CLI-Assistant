# Release Notes - v0.3.0

## What's New

### 🔄 Workflow Automation System

The biggest feature in this release! Automate repetitive system administration tasks with pre-built workflow templates.

#### New Commands

```bash
# List available workflows
nexus workflow list

# Run a system health check
nexus workflow run system-health

# Run with verbose output
nexus workflow run security-audit --verbose

# Show workflow details
nexus workflow show docker-health

# Create custom workflow from template
nexus workflow create my-check --from-template system-health
```

#### Pre-Built Templates

Five workflow templates are automatically installed:

1. **system-health** - Quick system health overview
   - Disk usage, memory, CPU load
   - Running and failed services
   - Perfect for daily system checks

2. **security-audit** - Security-focused checks
   - System updates available
   - Failed login attempts
   - Open ports and firewall status
   - SSH configuration
   - Sudo users

3. **performance-check** - System performance metrics
   - Top processes by CPU and memory
   - I/O statistics
   - Network socket statistics
   - Load average

4. **docker-health** - Docker and container status
   - Docker version and service status
   - Running containers
   - Container resource usage
   - Docker disk usage

5. **network-diagnostics** - Network connectivity checks
   - Interface status
   - Default gateway
   - DNS resolution
   - Internet connectivity
   - Listening ports

#### Workflow Features

- **Sequential Execution**: Commands run in order with proper error handling
- **Output Capture**: See results from each step
- **Error Handling**: Continue on error or stop execution
- **Variable Substitution**: Use `${VARIABLE}` in commands
- **Alternative Commands**: Fallback commands if primary fails
- **Timeout Protection**: Prevent commands from hanging
- **Verbose Mode**: See step-by-step progress

#### Creating Custom Workflows

Workflows are YAML files stored in `~/.config/nexus/workflows/user/`. You can:

1. **Create from template**: Copy and customize existing templates
   ```bash
   nexus workflow create my-workflow --from-template system-health
   ```

2. **Create from scratch**: Start with an empty workflow
   ```bash
   nexus workflow create my-workflow
   ```

3. **Edit workflows**: Modify YAML files directly to customize behavior

#### Use Cases

Perfect for:
- Daily system health checks
- Security audits
- Performance monitoring
- Docker container management
- Network diagnostics
- Custom automation tasks

## Installation

Update from v0.2.0:
```bash
cd nexus-cli-assistant
git pull
source venv/bin/activate
pip install -e .
```

The installation script will automatically install workflow templates to `~/.config/nexus/workflows/templates/`.

Or fresh install:
```bash
git clone https://github.com/nexus-mike/Nexus-CLI-Assistant.git
cd nexus-cli-assistant
./scripts/install.sh
```

## Breaking Changes

None - this is a backward-compatible update. All existing commands continue to work as before.

## What's Next

This release focuses on workflow automation. Future releases may include:
- More workflow templates
- Workflow scheduling (cron/systemd integration)
- Workflow sharing and export/import
- Workflow execution history
- Conditional workflow steps based on previous results

## Contributors

- Maikel van den Brink

## Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.
