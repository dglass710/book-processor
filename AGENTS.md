# Agent Guidelines

Use `CODE_REFERENCE.md` to familiarize yourself with the repository's modules, classes, and functions.

## Development workflow
- Ensure changes remain cross-platform (Windows, macOS, Linux) and compatible with Python 3.12.
- Provide docstrings for all new public functions and classes.
- Keep imports clean and sorted.
- Do not commit generated assets such as images, text output, or zip archives.

## Style and checks
Before committing, run the test suite from the repository root and fix any issues it reports:

```bash
python run_tests.py
```

This will run all code quality checks (isort, black, flake8, pyright) and unit tests.

If tests are added under a `tests/` directory, run `pytest` as well.

## Documentation
Update `README.md` or other documentation when you introduce user facing changes or new scripts.
