#!/usr/bin/env python3
"""
Push configuration to Moku device (direct deployment).

WARNING: Force connects and overwrites existing state without prompts!

Usage:
    python scripts/push.py <config.yaml> <device-ip> [-b BITSTREAM]

Examples:
    python scripts/push.py deployment.yaml 192.168.1.100
    python scripts/push.py config.json 192.168.1.100
    python scripts/push.py examples/01-basic.json 192.168.1.100 -b ./my_bitstream.tar
"""

import argparse
import json
import sys
from pathlib import Path

import yaml

# Add project root to path (standalone library structure)
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from moku_models import MokuConfig
from moku_models import (
    MOKU_GO_PLATFORM,
    MOKU_LAB_PLATFORM,
    MOKU_PRO_PLATFORM,
    MOKU_DELTA_PLATFORM,
)

try:
    from moku.instruments import MultiInstrument, CloudCompile, Oscilloscope
except ImportError:
    print("Error: moku library not installed. Run: uv sync")
    sys.exit(1)


def load_config(config_path: Path) -> MokuConfig:
    """Load MokuConfig from file."""
    content = config_path.read_text()
    
    if config_path.suffix.lower() in ['.yaml', '.yml']:
        data = yaml.safe_load(content)
    else:
        data = json.loads(content)
    
    # Handle string platform identifiers
    if isinstance(data.get('platform'), str):
        platform_map = {
            'moku_go': MOKU_GO_PLATFORM,
            'moku_lab': MOKU_LAB_PLATFORM,
            'moku_pro': MOKU_PRO_PLATFORM,
            'moku_delta': MOKU_DELTA_PLATFORM,
        }
        platform_str = data['platform'].lower()
        if platform_str in platform_map:
            data['platform'] = platform_map[platform_str].model_dump()
        else:
            raise ValueError(f"Unknown platform: {platform_str}")
    
    return MokuConfig.model_validate(data)


def main():
    parser = argparse.ArgumentParser(
        description='Push configuration to Moku device (force connect, overwrites state)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple positional syntax:
  %(prog)s config.yaml 192.168.1.100
  %(prog)s examples/01-basic.json 192.168.1.100 -b ./bitstream.tar

  # Flag-based syntax:
  %(prog)s -c config.yaml -i 192.168.1.100
  %(prog)s -c examples/01-basic.json -i 192.168.1.100 -b ./bitstream.tar
        """
    )

    # Positional arguments (can also use flags)
    parser.add_argument(
        'config_file',
        type=Path,
        nargs='?',
        help='Path to configuration file (YAML or JSON)'
    )
    parser.add_argument(
        'device_ip',
        type=str,
        nargs='?',
        help='Device IP address (e.g., 192.168.1.100)'
    )

    # Optional flag-based arguments
    parser.add_argument(
        '-c', '--config',
        type=Path,
        dest='config_flag',
        help='Config file (alternative to positional argument)'
    )
    parser.add_argument(
        '-i', '--ip',
        type=str,
        dest='ip_flag',
        help='Device IP (alternative to positional argument)'
    )
    parser.add_argument(
        '-b', '--bitstream',
        type=Path,
        default=None,
        help='Override bitstream path (replaces path in config)'
    )

    args = parser.parse_args()

    # Determine config path (flag takes precedence over positional)
    config_path = args.config_flag if args.config_flag else args.config_file
    if not config_path:
        parser.error("Config file required (provide as positional arg or use -c)")

    # Determine device IP (flag takes precedence over positional)
    device_ip = args.ip_flag if args.ip_flag else args.device_ip
    if not device_ip:
        parser.error("Device IP required (provide as positional arg or use -i)")

    bitstream_override = args.bitstream

    if not config_path.exists():
        print(f"Error: Config file not found: {config_path}")
        sys.exit(1)
    
    # Load config
    print(f"Loading config from {config_path}...")
    config = load_config(config_path)
    
    # Determine platform_id
    platform_name = config.platform.name
    platform_id_map = {
        "Moku:Go": 2,
        "Moku:Lab": 1,
        "Moku:Pro": 3,
        "Moku:Delta": 4,
    }
    platform_id = platform_id_map.get(platform_name, 2)
    
    # Connect to device (force connect, no persist state)
    print(f"Connecting to {device_ip}...")
    moku = MultiInstrument(
        device_ip,
        platform_id=platform_id,
        force_connect=True,  # Force disconnect all
        persist_state=False  # Don't preserve state
    )
    print("  ✓ Connected")
    
    try:
        # Deploy instruments
        print("\nDeploying instruments...")
        deployed_slots = set()  # Track which slots were successfully deployed
        for slot_num, slot_config in config.slots.items():
            if slot_config.instrument == 'CloudCompile':
                # Determine bitstream path (override or config)
                if bitstream_override:
                    bitstream_path = bitstream_override
                    print(f"  Using override bitstream: {bitstream_path}")
                elif slot_config.bitstream:
                    bitstream_path = Path(slot_config.bitstream)
                else:
                    print(f"  Slot {slot_num}: CloudCompile (no bitstream specified, skipping)")
                    continue

                # Resolve bitstream path (relative to project root or absolute)
                if not bitstream_path.is_absolute():
                    bitstream_path = PROJECT_ROOT / bitstream_path

                # Check if bitstream exists (skip if placeholder path)
                if not bitstream_path.exists():
                    print(f"  Slot {slot_num}: CloudCompile")
                    print(f"    ⚠ Warning: Bitstream not found: {bitstream_path}")
                    print(f"    ℹ Skipping CloudCompile deployment (use -b to provide bitstream)")
                    continue
                
                print(f"  Slot {slot_num}: CloudCompile ({bitstream_path.name})")
                cc = moku.set_instrument(slot_num, CloudCompile, bitstream=str(bitstream_path))
                deployed_slots.add(slot_num)
                
                # Apply control registers if specified
                if slot_config.control_registers:
                    for reg_num, reg_value in sorted(slot_config.control_registers.items()):
                        try:
                            cc.set_control(reg_num, reg_value)
                        except Exception as e:
                            print(f"    ⚠ Warning: CR{reg_num} = {e}")
            
            elif slot_config.instrument == 'Oscilloscope':
                print(f"  Slot {slot_num}: Oscilloscope")
                osc = moku.set_instrument(slot_num, Oscilloscope)
                deployed_slots.add(slot_num)
                
                # Configure frontend (input channels)
                if slot_config.settings:
                    # Filter out sample_rate (not a valid set_frontend parameter)
                    # Sample rate is platform-dependent and set automatically
                    frontend_settings = {
                        k: v for k, v in slot_config.settings.items()
                        if k != 'sample_rate'
                    }
                    
                    if frontend_settings:
                        try:
                            osc.set_frontend(1, **frontend_settings)
                        except Exception as e:
                            print(f"    ⚠ Warning: Settings = {e}")
                    
                    # Note: sample_rate is platform-dependent and cannot be set directly
                    # It's determined by the Moku device (e.g., 125 MSa/s for Moku:Go)
                    if 'sample_rate' in slot_config.settings:
                        print(f"    ℹ Note: sample_rate is platform-dependent (not configurable)")
                
                # Configure waveform generator output (if specified)
                # Note: waveform_output is an optional extended field (not validated by Pydantic)
                if hasattr(slot_config, 'waveform_output') and slot_config.waveform_output:
                    waveform_config = slot_config.waveform_output
                    try:
                        channel = waveform_config.get('channel', 1)
                        enable = waveform_config.get('enable', True)
                        waveform_type = waveform_config.get('waveform_type', 'Square')
                        frequency = waveform_config.get('frequency', 1000)
                        amplitude = waveform_config.get('amplitude', 2.5)
                        offset = waveform_config.get('offset', 1.25)
                        duty = waveform_config.get('duty', None)  # Optional, for square waves
                        
                        if enable:
                            # Configure waveform generator output using Oscilloscope's built-in generator
                            # Moku API: generate_waveform(channel, type, amplitude=..., frequency=..., offset=..., duty=...)
                            # Note: waveform_type should be capitalized (e.g., 'Sine', 'Square', 'Triangle')
                            kwargs = {
                                'amplitude': amplitude,
                                'frequency': frequency,
                            }
                            if offset is not None:
                                kwargs['offset'] = offset
                            # Square waves require duty cycle parameter (even if not specified)
                            if waveform_type.lower() == 'square':
                                kwargs['duty'] = duty if duty is not None else 50  # Default 50% duty cycle
                            
                            osc.generate_waveform(channel, waveform_type, **kwargs)
                            print(f"    ✓ Waveform Generator Output{channel}: {waveform_type} @ {frequency} Hz, {amplitude}V amplitude", end="")
                            if offset is not None:
                                print(f", {offset}V offset", end="")
                            if waveform_type.lower() == 'square':
                                # Always show duty cycle for square waves
                                duty_value = duty if duty is not None else 50
                                print(f", {duty_value}% duty", end="")
                            print()
                        else:
                            print(f"    ℹ Waveform Generator Output{channel}: disabled")
                    except Exception as e:
                        print(f"    ⚠ Warning: Waveform generator configuration failed: {e}")
                        print(f"    ℹ Note: Check that waveform_type is valid (e.g., 'Sine', 'Square', 'Triangle')")
            
            else:
                print(f"  Slot {slot_num}: {slot_config.instrument} (not implemented, skipping)")
        
        # Configure routing (filter out connections to non-deployed slots)
        if config.routing:
            print("\nConfiguring routing...")

            # Helper to check if a port references a deployed slot
            def is_port_available(port_name: str) -> bool:
                # Physical ports are always available
                if port_name.startswith(('Input', 'Output')):
                    return True
                # Slot ports - check if slot was deployed
                if port_name.startswith('Slot'):
                    slot_num = int(port_name[4])  # Extract slot number
                    return slot_num in deployed_slots
                return True

            # Filter routing to only include connections with deployed endpoints
            valid_connections = []
            skipped_connections = []
            for conn in config.routing:
                if is_port_available(conn.source) and is_port_available(conn.destination):
                    valid_connections.append({'source': conn.source, 'destination': conn.destination})
                else:
                    skipped_connections.append(f"{conn.source} → {conn.destination}")

            if skipped_connections:
                print(f"  ℹ Skipping {len(skipped_connections)} connection(s) (slots not deployed):")
                for skipped in skipped_connections:
                    print(f"    - {skipped}")

            if valid_connections:
                moku.set_connections(valid_connections)
                print(f"  ✓ {len(valid_connections)} connections configured")
            else:
                print(f"  ℹ No valid connections to configure")
        
        print("\n✓ Deployment complete")
    
    finally:
        # Disconnect
        try:
            moku.relinquish_ownership()
            print("  ✓ Disconnected")
        except Exception as e:
            print(f"  ⚠ Warning: {e}")


if __name__ == "__main__":
    main()
