# Agent Guidelines

Use `CODE_REFERENCE.md` to familiarize yourself with the repository's modules, classes, and functions.

## Development workflow
- Ensure changes remain cross-platform (Windows, macOS, Linux) and compatible with Python 3.12.
- Provide docstrings for all new public functions and classes.
- Keep imports clean and sorted.
- Do not commit generated assets such as images, text output, or zip archives.

## Testing and Code Quality
Before committing any changes, it is **mandatory** to run our comprehensive testing suite from the repository root:

```bash
python run_tests.py
```

This unified testing script performs:
- **Code Formatting**: Runs `isort` and `black` to ensure consistent code style
- **Linting**: Executes `flake8` to catch common programming errors
- **Type Checking**: Uses `pyright` for static type analysis
- **Unit Tests**: Runs all `pytest` tests in the `tests/` directory

All checks must pass before committing changes. The script will provide detailed feedback for any issues found.

## Documentation
Update `README.md` or other documentation when you introduce user facing changes or new scripts.
