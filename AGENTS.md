# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

AEGIS is a Python 3.13 project using [uv](https://github.com/astral-sh/uv) for fast, reliable package management.

## Development Environment

### Setup

**First-time setup:**
```powershell
# Install uv (if not already installed)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Add uv to PATH for current session
$env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"

# Install dependencies
uv sync --group dev
```

### Common Commands

**Package Management:**
```powershell
# Sync dependencies (install/update)
uv sync

# Install with dev dependencies
uv sync --group dev

# Add a new dependency
uv add <package-name>

# Add a dev dependency
uv add --group dev <package-name>

# Remove a dependency
uv remove <package-name>
```

**Running the Application:**
```powershell
# Run the main application
uv run aegis

# Run any Python script
uv run python src/aegis/main.py
```

**Testing:**
```powershell
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_main.py

# Run with coverage
uv run pytest --cov=aegis --cov-report=html

# Run tests in watch mode (if pytest-watch is installed)
uv run ptw
```

**Code Quality:**
```powershell
# Format code with black (when configured)
uv run black src/ tests/

# Lint with ruff (when configured)
uv run ruff check src/ tests/

# Type checking with mypy (when configured)
uv run mypy src/
```

## Project Structure

```
AEGIS/
├── src/
│   └── aegis/         # Main application package
│       ├── __init__.py
│       └── main.py
├── tests/             # Test files
│   └── test_main.py
├── .venv/             # Virtual environment (managed by uv)
├── pyproject.toml     # Project configuration and dependencies
├── .python-version    # Python version specification (3.13)
├── uv.lock            # Locked dependency versions
├── .gitignore
├── AGENTS.md
├── LICENSE
└── README.md
```

## Development Guidelines

- Python 3.13 is the target version
- Use `uv` for all package management (not pip)
- All source code goes in `src/aegis/`
- All tests go in `tests/`
- Use `uv run` prefix for running commands to ensure correct environment
- Follow PEP 8 style guidelines
- Write tests for new functionality
