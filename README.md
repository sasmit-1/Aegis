# AEGIS

A Python 3.13 application built with [uv](https://github.com/astral-sh/uv).

## Setup

1. Install dependencies:
```bash
uv sync
```

2. Run the application:
```bash
uv run aegis
```

## Development

### Install development dependencies
```bash
uv sync --group dev
```

### Run tests
```bash
uv run pytest
```

### Run tests with coverage
```bash
uv run pytest --cov=aegis --cov-report=html
```

## Project Structure

```
AEGIS/
├── src/
│   └── aegis/         # Main package
│       ├── __init__.py
│       └── main.py
├── tests/             # Test files
│   └── test_main.py
├── pyproject.toml     # Project configuration
├── .python-version    # Python version (3.13)
└── README.md
```