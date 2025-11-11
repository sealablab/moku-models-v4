#!/usr/bin/env python3
"""
Push configuration to a Moku device (overwrites existing config).

Simple CLI wrapper around moku_models.device.push_config()

WARNING: This will overwrite the currently running configuration on the device!
"""

import argparse
import json
import sys
from pathlib import Path

# Add parent directory to path for local imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from moku_models import MokuConfig
from moku_models.device import push_config


def main():
    parser = argparse.ArgumentParser(
        description='Push configuration to a Moku device (overwrites existing)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
WARNING: This will overwrite the currently running configuration!

Examples:
  %(prog)s --ip 192.168.1.100 --config deployment.json
  %(prog)s --ip 192.168.1.100 --config deployment.json --platform go
  %(prog)s --ip 192.168.1.100 --config deployment.json --yes
        """
    )

    parser.add_argument(
        '--ip',
        required=True,
        help='Device IP address'
    )
    parser.add_argument(
        '--config',
        type=Path,
        required=True,
        help='Configuration file (JSON format)'
    )
    parser.add_argument(
        '--platform',
        choices=['go', 'lab', 'pro'],
        help='Device platform (auto-detected if not specified)'
    )
    parser.add_argument(
        '--yes', '-y',
        action='store_true',
        help='Skip confirmation prompt'
    )

    args = parser.parse_args()

    # Load configuration
    if not args.config.exists():
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)

    try:
        with open(args.config) as f:
            config_dict = json.load(f)

        # Validate config BEFORE pushing (safety check)
        from moku_models import validate_config_dict
        print("Validating configuration...")
        valid, msg, _ = validate_config_dict(config_dict)

        if not valid:
            print(f"\n❌ Configuration validation failed:")
            print(msg)
            print("\nRefusing to push invalid configuration to device.")
            sys.exit(1)

        print(msg)

        # Confirm before proceeding (unless --yes)
        if not args.yes:
            print(f"\n⚠️  WARNING: This will OVERWRITE the current configuration on {args.ip}!")
            print(f"Configuration file: {args.config}")
            if 'slots' in config_dict:
                print(f"Slots to deploy: {list(config_dict['slots'].keys())}")
            response = input("\nProceed? [y/N] ")
            if response.lower() not in ['y', 'yes']:
                print("Cancelled.")
                sys.exit(0)

        print(f"\nPushing configuration to {args.ip}...")
        push_config(
            ip=args.ip,
            config=config_dict,
            platform=args.platform,
            overwrite=True  # Required safety parameter
        )

        print("✓ Configuration deployed successfully!")

    except ImportError as e:
        print(f"Error: {e}")
        print("Install required package: pip install moku")
        sys.exit(1)
    except ValueError as e:
        if "overwrite" in str(e):
            print(f"Safety Error: {e}")
            sys.exit(1)
        raise
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
