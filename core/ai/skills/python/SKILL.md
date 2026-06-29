---
name: python-coding-standards
description: Python coding standards following PEP 8, Google Python Style Guide, and modern Python best practices. Covers formatting, type hints, code organization, error handling, classes, testing, and virtual environments. Use when writing or reviewing Python code.
---

# Python Coding Standards

These rules follow PEP 8, Google Python Style Guide, and modern Python best practices.

## Formatting and Style

### Use Standard Tools
- Format code with `black` or `yapf`
- Sort imports with `isort`
- Lint with `pylint`, `flake8`, or `ruff`
- Type check with `mypy` or `pyright`

### Indentation and Line Length
- Use 4 spaces for indentation (never tabs)
- Maximum line length: 88-100 characters (per project convention)
- Use parentheses for line continuation, not backslashes

### Naming Conventions
- `snake_case` for functions, methods, variables, modules
- `PascalCase` for classes
- `UPPER_SNAKE_CASE` for constants
- `_single_leading_underscore` for internal/private
- Avoid single-letter names except for loop counters or math

## Type Hints

### Always Use Type Hints
- Add type hints to all public functions and methods
- Use type hints for class attributes
- Import types from `typing` module for complex types

```python
from typing import Optional, List, Dict, Union

def process_items(items: List[str], config: Optional[Dict[str, str]] = None) -> bool:
    ...
```

### Modern Type Hint Syntax (Python 3.10+)
```python
# Use built-in types directly (Python 3.9+)
def process(items: list[str]) -> dict[str, int]:
    ...

# Use union with | (Python 3.10+)
def find(value: int | str | None) -> str:
    ...
```

## Code Organization

### Import Order
1. Standard library imports
2. Related third-party imports
3. Local application/library imports

```python
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd

from myproject.utils import helper
from myproject.models import User
```

### Module Structure
- Keep modules focused; one primary purpose per module
- Use `__all__` to define public API
- Place imports at top of file
- Constants after imports, classes next, then functions

## Error Handling

### Exception Best Practices
- Catch specific exceptions, not bare `except:`
- Use `raise ... from err` to preserve exception chains
- Create custom exceptions for domain-specific errors
- Use context managers (`with`) for resource management

```python
# Good
try:
    process_file(path)
except FileNotFoundError as e:
    logger.error(f"File not found: {path}")
    raise ConfigurationError(f"Missing config file: {path}") from e

# Bad
try:
    process_file(path)
except:  # Too broad
    pass  # Silent failure
```

### Context Managers
```python
# Always use context managers for resources
with open("file.txt") as f:
    content = f.read()

# For multiple resources
with open("input.txt") as inp, open("output.txt", "w") as out:
    out.write(inp.read())
```

## Classes and Functions

### Function Design
- Keep functions small and focused
- Use keyword arguments for clarity with many parameters
- Avoid mutable default arguments

```python
# Bad: Mutable default argument
def append_to(element, lst=[]):  # Bug: shared list!
    lst.append(element)
    return lst

# Good: Use None as default
def append_to(element, lst=None):
    if lst is None:
        lst = []
    lst.append(element)
    return lst
```

### Class Design
- Use `@dataclass` for data containers
- Use `@property` for computed attributes
- Prefer composition over inheritance
- Use `__slots__` for memory-efficient classes with many instances

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    email: str
    active: bool = True
```

## Testing

### Test Structure
- Use `pytest` as the testing framework
- Test files: `test_*.py` or `*_test.py`
- Test functions: `test_<what>_<scenario>`
- Use fixtures for common setup

### Pytest Best Practices
```python
import pytest

@pytest.fixture
def sample_user():
    return User(name="Test", email="test@example.com")

def test_user_creation_with_defaults(sample_user):
    assert sample_user.active is True

@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("World", "WORLD"),
])
def test_uppercase(input, expected):
    assert input.upper() == expected
```

## Virtual Environments and Dependencies

### Environment Management
- Always use virtual environments
- Use `pyproject.toml` for modern projects
- Pin dependency versions in `requirements.txt` or `poetry.lock`
- Separate dev dependencies from production

### Requirements Files
```text
# requirements.txt - pin exact versions for reproducibility
requests==2.31.0
pydantic==2.5.0

# requirements-dev.txt
-r requirements.txt
pytest==7.4.0
black==23.12.0
mypy==1.7.0
```

## Common Pitfalls to Avoid

### Mutable Arguments and Closures
- Don't use mutable default arguments
- Be careful with late binding in closures

### String Formatting
- Use f-strings for simple interpolation
- Use `.format()` for complex cases or deferred formatting
- Never use `%` formatting in new code

### Comparisons
- Use `is` for `None`, `True`, `False` comparisons
- Use `==` for value comparisons
- Use `isinstance()` instead of `type()` for type checks
