# Workflow Templates

This directory contains pre-built workflow templates for common system administration tasks.

## Available Templates

### system-health.yaml
Quick system health check - monitors disk, memory, CPU, and services.

**Usage:**
```bash
nexus workflow run system-health
```

**What it checks:**
- Disk usage on root filesystem
- Memory usage
- CPU load average
- Running services
- Failed services

### security-audit.yaml
Security-focused checks including updates, failed logins, open ports, and firewall status.

**Usage:**
```bash
nexus workflow run security-audit
```

**What it checks:**
- Available system updates
- Failed login attempts
- Listening ports
- Users with sudo privileges
- Firewall status (UFW or iptables)
- SSH security configuration

### performance-check.yaml
System performance metrics including top processes, I/O stats, and network statistics.

**Usage:**
```bash
nexus workflow run performance-check
```

**What it checks:**
- Top processes by CPU usage
- Top processes by memory usage
- I/O statistics
- Network socket statistics
- System load average

### docker-health.yaml
Docker and container status checks.

**Usage:**
```bash
nexus workflow run docker-health
```

**What it checks:**
- Docker version
- Docker service status
- Running containers
- Container resource usage
- Docker disk usage

### network-diagnostics.yaml
Network connectivity and configuration checks.

**Usage:**
```bash
nexus workflow run network-diagnostics
```

**What it checks:**
- Network interface status
- Default gateway
- DNS resolution
- Internet connectivity
- Listening ports

## Creating Custom Templates

Copy any template to `~/.config/nexus/workflows/user/` and modify it to create your own workflows.

**Example:**
```bash
cp ~/.config/nexus/workflows/templates/system-health.yaml ~/.config/nexus/workflows/user/my-custom-check.yaml
# Edit the file to customize it
```

## Template Structure

Each template is a YAML file with the following structure:

```yaml
name: "workflow-name"
version: "1.0.0"
description: "Description of what the workflow does"
category: "category-name"
tags:
  - tag1
  - tag2

steps:
  - name: "step-name"
    command: "command to run"
    description: "What this step does"
    shell: false
    capture_output: true
    continue_on_error: false
    timeout: 5

output_format: "summary"
estimated_duration: "10-15 seconds"
```

### Shell execution

By default, workflow steps run without a shell (`shell: false`). If you need shell features
like pipes or redirection, explicitly set `shell: true` on the step. When shell execution
is enabled, variable substitutions are escaped with `shlex.quote(...)` before being injected
into the command to reduce the risk of unintended command execution.

## Updating Templates

Templates are updated when you upgrade the package. Your custom templates in the `user/` directory are never overwritten.

## Contributing

If you create useful workflow templates, consider contributing them back to the project!
