"""
Pull configuration from a running Moku device.

Reads the current configuration including control registers, instrument settings,
and routing information, then returns it as a MokuConfig object.
"""

from typing import Optional, Dict, Any
from pathlib import Path
import json

try:
    from moku import Moku
    from moku.instruments import CloudCompile
    from moku.exceptions import MokuException, MokuNotFound
    MOKU_AVAILABLE = True
except ImportError:
    MOKU_AVAILABLE = False


def _connect_to_device(ip_address: str, platform: str = 'auto'):
    """
    Connect to a Moku device.

    Uses the current moku library API (single Moku class that auto-detects platform).
    The 'platform' parameter is accepted for backwards compatibility but is not used.

    Args:
        ip_address: Device IP address
        platform: Ignored (kept for backwards compatibility)

    Returns:
        Tuple of (device, detected_platform_name)
    """
    if not MOKU_AVAILABLE:
        raise ImportError(
            "moku package not found. Install with: pip install moku"
        )

    # Connect using current API (auto-detects platform)
    # Use force_connect=True to take over existing connections if needed
    device = Moku(ip_address, force_connect=True, ignore_busy=True)

    # Try to detect platform from device properties
    detected_platform = 'unknown'
    try:
        if hasattr(device, 'platform'):
            detected_platform = device.platform.lower()
        elif hasattr(device, 'get_platform'):
            detected_platform = device.get_platform().lower()
    except:
        pass

    return device, detected_platform


def _read_control_registers(
    instrument,
    max_registers: int = 32
) -> Dict[int, int]:
    """Read control registers from a CloudCompile instrument."""
    if not isinstance(instrument, CloudCompile):
        return {}

    registers = {}
    for idx in range(max_registers):
        try:
            value = instrument.get_control(idx, strict=False)
            if value is not None and value != 0:
                registers[idx] = value
        except:
            break  # Stop at first error

    return registers


def pull_config(
    ip: str,
    platform: str = 'auto',
    save_to: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Pull current configuration from a running Moku device.

    Args:
        ip: Device IP address
        platform: Platform type ('go', 'lab', 'pro', 'auto')
        save_to: Optional path to save configuration as JSON

    Returns:
        Dictionary containing device configuration:
        - device_info: Platform, serial, IP, timestamp, firmware version
        - slots: Dictionary of slot configurations
        - control_registers: Dictionary of control register values per slot

    Example:
        >>> config = pull_config(ip='192.168.1.100')
        >>> print(config['device_info']['platform'])
        'MokuGo'
        >>> print(config['slots'][1]['instrument'])
        'CloudCompile'
        >>> print(config['control_registers']['slot_1'][0])
        0xE0000000

    Raises:
        ImportError: If moku package is not installed
        MokuException: If connection fails
    """
    from datetime import datetime

    # Connect to device
    device, detected_platform = _connect_to_device(ip, platform)

    try:
        # Read device info
        # Get IP from device object or fall back to input parameter
        ip_addr = getattr(device, 'ip', None) or getattr(device, 'ip_address', None) or ip

        config = {
            'device_info': {
                'serial_number': getattr(device, 'serial', 'Unknown'),
                'platform': type(device).__name__,
                'detected_platform': detected_platform,
                'ip_address': ip_addr,
                'timestamp': datetime.now().isoformat(),
            },
            'slots': {},
            'control_registers': {},
        }

        # Try to get firmware version
        try:
            config['device_info']['firmware_version'] = device.get_firmware_version()
        except:
            config['device_info']['firmware_version'] = 'Unknown'

        # Read slot information
        max_slots = 4  # Try up to 4 slots
        for slot_num in range(1, max_slots + 1):
            try:
                instrument = device.discover_instrument(slot=slot_num)
                if instrument:
                    instrument_name = type(instrument).__name__
                    config['slots'][slot_num] = {
                        'instrument': instrument_name,
                        'running': True
                    }

                    # Read control registers if CloudCompile
                    registers = _read_control_registers(instrument)
                    if registers:
                        config['control_registers'][f'slot_{slot_num}'] = registers
            except:
                break  # Stop at first invalid slot

        # Save to file if requested
        if save_to:
            with open(save_to, 'w') as f:
                json.dump(config, f, indent=2)

        return config

    finally:
        # Clean up connection
        # Current API supports context manager (__exit__)
        if hasattr(device, '__exit__'):
            device.__exit__(None, None, None)
