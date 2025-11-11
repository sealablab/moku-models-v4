#!/usr/bin/env python3
"""
Validate MokuConfig YAML/JSON files against Pydantic models.

Usage:
    # Validate YAML file
    uv run python scripts/validate_moku_config.py deployment.yaml

    # Validate JSON file
    uv run python scripts/validate_moku_config.py config.json

    # With verbose output
    uv run python scripts/validate_moku_config.py deployment.yaml --verbose

Supported Formats:
    - YAML (.yaml, .yml)
    - JSON (.json)

Cascading pyproject.toml Strategy:
    This script works with the monorepo's two-tier testing strategy:

    - Tier 1 (Component): Run from libs/moku-models/ with minimal dependencies
      (pydantic + pyyaml, fastest installation)

    - Tier 2 (Integration): Run from monorepo root with full workspace
      (all workspace members available for cross-library validation)

    See: Obsidian/Project/Review/CASCADING_PYPROJECT_STRATEGY.md
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from moku_models import load_and_validate_config


def main():
    parser = argparse.ArgumentParser(
        description='Validate MokuConfig YAML/JSON files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s deployment.yaml
  %(prog)s config.json
  %(prog)s deployment.yaml --verbose
        """
    )

    parser.add_argument(
        'config_file',
        type=Path,
        help='Path to config file (YAML or JSON)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation warnings'
    )

    args = parser.parse_args()

    if not args.config_file.exists():
        print(f"Error: File not found: {args.config_file}")
        sys.exit(1)

    # Use shared validation logic
    success, message, _ = load_and_validate_config(
        args.config_file,
        verbose=args.verbose
    )

    print(message)
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
