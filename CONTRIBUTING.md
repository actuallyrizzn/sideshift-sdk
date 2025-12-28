# Contributing to SideShift SDK

Thank you for your interest in contributing to the SideShift SDK! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or suggest features
- Include as much detail as possible: Python version, SDK version, error messages, steps to reproduce
- Check existing issues before creating a new one

### Submitting Pull Requests

1. **Fork the repository** and create a new branch from `main`
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the existing code style (black formatter, line length 100)
   - Add tests for new functionality
   - Update documentation as needed
   - Ensure all tests pass

3. **Run the test suite**
   ```bash
   pytest
   ```

4. **Run code formatting**
   ```bash
   black sideshift_sdk tests
   ```

5. **Run linting**
   ```bash
   ruff check sideshift_sdk tests
   ```

6. **Run type checking**
   ```bash
   mypy sideshift_sdk
   ```

7. **Commit your changes**
   - Use clear, descriptive commit messages
   - Reference issue numbers when applicable

8. **Push and create a Pull Request**
   - Provide a clear description of your changes
   - Link to any related issues
   - Ensure CI checks pass

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/actuallyrizzn/sideshift-sdk.git
   cd sideshift-sdk
   ```

2. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

3. Install pre-commit hooks (if configured):
   ```bash
   pre-commit install
   ```

## Code Style

- **Formatting**: Use `black` with line length 100
- **Linting**: Follow `ruff` rules
- **Type Hints**: Use type hints throughout the codebase
- **Docstrings**: Follow Google-style docstrings with examples where appropriate
- **Imports**: Use absolute imports, group by standard library, third-party, local

## Testing

- Write tests for all new functionality
- Aim for high test coverage
- Use descriptive test names
- Test both success and error cases

## Documentation

- Update README.md for user-facing changes
- Update docstrings for API changes
- Add examples for new features
- Update CHANGELOG.md for significant changes

## Release Process

Releases are managed by maintainers. Version numbers follow [Semantic Versioning](https://semver.org/).

## Questions?

Feel free to open an issue for questions or clarification about contributing.

