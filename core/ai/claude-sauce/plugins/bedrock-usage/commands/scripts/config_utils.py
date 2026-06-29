#!/usr/bin/env python3
"""
Shared configuration utilities for Claude Sauce Bedrock plugins.

Provides structured error messages for missing credentials that Claude can
detect and automate setup for.
"""

import sys


def print_setup_instructions(service_name, config_keys, token_generation_url=None):
    """
    Print structured error message when credentials are missing.
    Claude will detect this pattern and automate the setup process.

    Args:
        service_name: Name of the service (e.g., 'bedrock')
        config_keys: Dict of required config keys and their descriptions
        token_generation_url: Optional URL to token generation page
    """
    print("\n" + "=" * 80, file=sys.stderr)
    print(f"MISSING CREDENTIALS: {service_name.upper()}", file=sys.stderr)
    print("=" * 80, file=sys.stderr)
    print(f"\nThe {service_name} integration requires credentials in ~/.claude-sauce.json", file=sys.stderr)

    # Print required keys (for Claude to parse)
    print(f"\nRequired configuration keys:", file=sys.stderr)
    for key, description in config_keys.items():
        print(f"  - {key}: {description}", file=sys.stderr)

    # Token generation URL (for Claude to offer opening)
    if token_generation_url:
        print(f"\nToken generation URL: {token_generation_url}", file=sys.stderr)

    print("\n" + "=" * 80, file=sys.stderr)
