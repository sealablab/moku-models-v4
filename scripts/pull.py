#!/usr/bin/env python3
"""
Pull configuration from a running Moku device.

Simple CLI wrapper around moku_models.device.pull_config()
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from moku_models.device import pull_config


def main():
    parser = argparse.ArgumentParser(
        description='Pull configuration from a running Moku device',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --ip 192.168.1.100
  %(prog)s --ip 192.168.1.100 --output config.json
  %(prog)s --ip 192.168.1.100 --platform go
        """
    )

    parser.add_argument(
        '--ip',
        required=True,
        help='Device IP address'
    )
    parser.add_argument(
        '--platform',
        default='auto',
        choices=['auto', 'go', 'lab', 'pro'],
        help='Device platform (default: auto-detect)'
    )
    parser.add_argument(
        '--output', '-o',
        type=Path,
        help='Output file path (JSON format)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate pulled configuration against Pydantic models'
    )

    args = parser.parse_args()

    try:
        print(f"Connecting to device at {args.ip}...")
        config = pull_config(
            ip=args.ip,
            platform=args.platform,
            save_to=args.output
        )

        # Optionally validate pulled config
        if args.validate:
            from moku_models import validate_config_dict
            print("\nValidating pulled configuration...")
            valid, msg, _ = validate_config_dict(config)
            print(msg)
            if not valid:
                print("\n⚠️  Warning: Pulled configuration failed validation!")
                print("This may indicate:")
                print("  - Device is in unexpected state")
                print("  - Unsupported configuration detected")
                print("  - Model definitions need updating")

        if args.output:
            print(f"\n✓ Configuration saved to {args.output}")
        else:
            print("\n" + "="*60)
            print("DEVICE CONFIGURATION")
            print("="*60)
            print(json.dumps(config, indent=2))

    except ImportError as e:
        print(f"Error: {e}")
        print("Install required package: pip install moku")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
