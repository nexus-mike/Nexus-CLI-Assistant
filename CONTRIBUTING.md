# Contributing to Nexus CLI Assistant

Thank you for your interest in contributing to Nexus CLI Assistant! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant error messages or logs

### Suggesting Features

Feature suggestions are welcome! Please open an issue with:
- A clear description of the feature
- Use cases and examples
- Any potential implementation ideas (optional)

### Submitting Code Changes

1. **Fork the repository** on GitHub
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes** following the coding standards below
4. **Test your changes** thoroughly
5. **Commit your changes** with clear, descriptive messages:
   ```bash
   git commit -m "Add: description of your change"
   ```
6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Open a Pull Request** on GitHub with:
   - A clear title and description
   - Reference to any related issues
   - Screenshots or examples if applicable

## Coding Standards

### Python Style

- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Keep functions focused and small
- Add docstrings to functions and classes
- Maximum line length: 100 characters (where reasonable)

### Code Organization

- Keep related functionality together
- Use meaningful variable and function names
- Add comments for complex logic
- Follow existing code patterns

### Testing

- Test your changes locally
- Ensure existing functionality still works
- Test edge cases and error handling

## Development Setup

1. Clone your fork:
   ```bash
   git clone https://github.com/nexus-mike/Nexus-CLI-Assistant.git
   cd nexus-cli-assistant
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. Make your changes and test them

## Pull Request Process

1. Ensure your code follows the coding standards
2. Update documentation if needed
3. Add tests if applicable
4. Ensure all tests pass
5. Request review from maintainers

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

## Questions?

If you have questions, feel free to:
- Open an issue for discussion
- Start a discussion in GitHub Discussions (if enabled)

Thank you for contributing! 🎉

