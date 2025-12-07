# Contributing to VCF Contact Merger

First off, thanks for taking the time to contribute! 🎉

The following is a set of guidelines for contributing to VCF Contact Merger. These are mostly guidelines, not rules. Use your best judgment, and feel free to propose changes to this document in a pull request.

## Code of Conduct

This project and everyone participating in it is governed by the [VCF Contact Merger Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [vcfmerger mail](mailto:faisalmoshiur+vcfmerger@gmail.com).

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

- **Use the Bug Report Template**: We have a template for bug reports in `.github/ISSUE_TEMPLATE/bug_report.md`. Please use it.
- **Check for Existing Issues**: Before creating a new issue, please search the issue tracker to make sure the bug hasn't already been reported.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion, including completely new features and minor improvements to existing functionality.

- **Use the Feature Request Template**: We have a template for feature requests in `.github/ISSUE_TEMPLATE/feature_request.md`.
- **Be Specific**: Describe the feature you want in detail. Why do you need it? How should it work?

### Pull Requests

1.  **Fork the Repo**: Create a fork of the repository to your own GitHub account.
2.  **Create a Branch**: Create a new branch for your changes (`git checkout -b feature/amazing-feature`).
3.  **Code Style**: Ensure your code adheres to the project's coding standards (see below).
4.  **Test**: Run existing tests and add new ones for your changes.
5.  **Commit**: Make sure your commit messages are clear and descriptive.
6.  **Push**: Push your changes to your fork (`git push origin feature/amazing-feature`).
7.  **Open a PR**: Submit a pull request to the `main` branch.

## Development Guide

### Prerequisites

- Python 3.6 or later
- Git

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/fam007e/VCFmerger.git
cd VCFmerger

# Install in development mode with dev dependencies
pip install -e .[dev]
```

### Code Quality Standards

This project maintains high code quality standards. Before submitting a PR, please ensure:

1.  **Pylint**: Your code should score 10/10.
    ```bash
    pylint merge_script.py
    ```
2.  **Formatting**: We use `black` for code formatting.
    ```bash
    black merge_script.py
    ```
3.  **Type Checking**: We use `mypy` for static type checking.
    ```bash
    mypy merge_script.py
    ```
4.  **Linting**: We use `ruff` for fast linting.
    ```bash
    ruff check merge_script.py
    ```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=merge_script

# Run specific test
pytest test_*.py
```

## Documentation

- **Docstrings**: Ensure all functions, classes, and modules have clear docstrings.
- **README**: If you add a new feature, update the `README.md` to reflect the changes.

## License

By contributing, you agree that your contributions will be licensed under its MIT License.
