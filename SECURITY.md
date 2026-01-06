# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Which versions are eligible for receiving such patches depends on the CVSS v3.0 Rating:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

- **Email**: github@neural-nexus.net
- **GitHub Security Advisory**: Use the "Report a vulnerability" button on the repository's Security tab

Please include the following information:
- Type of vulnerability
- Full paths of source file(s) related to the vulnerability
- Location of the affected code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Best Practices

### For Users

1. **Never commit API keys or secrets**:
   - Use `.env` file (which is gitignored)
   - Use environment variables
   - Never hardcode credentials in code

2. **Keep dependencies updated**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

3. **Review configuration files**:
   - Check `~/.config/nexus/config.yaml` for sensitive data
   - Ensure proper file permissions (600 recommended)

4. **Use rate limiting**:
   - Configure appropriate rate limits to prevent abuse
   - Monitor API usage

### For Contributors

1. **Never commit secrets or API keys**
2. **Use `.env.example` for template values only**
3. **Sanitize any test data or examples**
4. **Review dependencies for security vulnerabilities**

## Disclosure Policy

When we receive a security bug report, we will:

1. Confirm the issue and determine affected versions
2. Audit code to find any potential similar problems
3. Prepare fixes for all releases still under support
4. Release a security update as soon as possible

We credit security researchers who responsibly disclose vulnerabilities.

