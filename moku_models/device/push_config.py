"""
Push configuration to a Moku device.

Deploys a MokuConfig to hardware, intentionally overwriting the current
running configuration. Use with caution!
"""

from typing import Optional, Union
from pathlib import Path

try:
    from moku import Moku
    from moku.instruments import CloudCompile
    from moku.exceptions import MokuException
    MOKU_AVAILABLE = True
except ImportError:
    MOKU_AVAILABLE = False


def _connect_to_device(ip_address: str, platform: str = None):
    """
    Connect to a Moku device.

    Uses the current moku library API (single Moku class that auto-detects platform).
    The 'platform' parameter is accepted for backwards compatibility but is not used.

    Args:
        ip_address: Device IP address
        platform: Ignored (kept for backwards compatibility)

    Returns:
        Moku device object
    """
    if not MOKU_AVAILABLE:
        raise ImportError(
            "moku package not found. Install with: pip install moku"
        )

    # Connect using current API (auto-detects platform)
    return Moku(ip_address, force_connect=True, ignore_busy=True)


def _deploy_slot(device, slot_num: int, slot_config):
    """Deploy a single slot configuration."""
    instrument_type = slot_config.get('instrument')

    if instrument_type == 'CloudCompile':
        # Deploy CloudCompile instrument
        bitstream = slot_config.get('bitstream')
        if not bitstream:
            raise ValueError(f"Slot {slot_num}: CloudCompile requires 'bitstream' field")

        if not Path(bitstream).exists():
            raise FileNotFoundError(f"Bitstream not found: {bitstream}")

        # Deploy the instrument
        instrument = device.deploy_instrument(slot=slot_num, instrument='CloudCompile')
        instrument.set_bitstream(bitstream)

        # Set control registers
        control_registers = slot_config.get('control_registers', {})
        for reg_idx, reg_value in control_registers.items():
            instrument.set_control(int(reg_idx), int(reg_value))

        return instrument

    else:
        # Deploy other instrument types
        instrument = device.deploy_instrument(slot=slot_num, instrument=instrument_type)

        # Apply settings if provided
        settings = slot_config.get('settings', {})
        for key, value in settings.items():
            # Use generic setattr for settings
            # Different instruments have different APIs
            try:
                setattr(instrument, key, value)
            except AttributeError:
                # Try as method call
                method = getattr(instrument, f'set_{key}', None)
                if method:
                    method(value)

        return instrument


def push_config(
    ip: str,
    config: Union[dict, 'MokuConfig'],
    platform: Optional[str] = None,
    overwrite: bool = False,
    force: bool = False
):
    """
    Push configuration to a Moku device, intentionally overwriting current config.

    **WARNING**: This will overwrite the currently running configuration on the device!
    Set overwrite=True to acknowledge this behavior.

    Args:
        ip: Device IP address
        config: MokuConfig object or dictionary containing configuration
        platform: Deprecated (kept for backwards compatibility, but ignored - API auto-detects)
        overwrite: Must be True to actually perform the push (safety check)
        force: Deprecated (connection always forces if busy)

    Example:
        >>> from moku_models import MokuConfig, SlotConfig
        >>>
        >>> config = MokuConfig(
        ...     platform=MOKU_GO_PLATFORM,
        ...     slots={
        ...         1: SlotConfig(
        ...             instrument='CloudCompile',
        ...             bitstream='my_instrument.tar',
        ...             control_registers={0: 0xE0000000}
        ...         )
        ...     }
        ... )
        >>>
        >>> # Safety check: must explicitly acknowledge overwrite
        >>> push_config(ip='192.168.1.100', config=config, overwrite=True)

    Raises:
        ValueError: If overwrite=False (safety check)
        ImportError: If moku package is not installed
        MokuException: If deployment fails
        FileNotFoundError: If bitstream file doesn't exist
    """
    # Safety check
    if not overwrite:
        raise ValueError(
            "Must set overwrite=True to push config to device. "
            "This will overwrite the current running configuration!"
        )

    # Convert MokuConfig to dict if needed
    if hasattr(config, 'model_dump'):
        # Pydantic v2
        config_dict = config.model_dump()
    elif hasattr(config, 'dict'):
        # Pydantic v1
        config_dict = config.dict()
    else:
        # Already a dict
        config_dict = config

    # Connect to device (API auto-detects platform, parameter ignored)
    device = _connect_to_device(ip, platform)

    try:
        # Deploy each slot
        slots = config_dict.get('slots', {})
        deployed_instruments = {}

        for slot_num, slot_config in slots.items():
            print(f"Deploying slot {slot_num}: {slot_config.get('instrument')}")
            instrument = _deploy_slot(device, int(slot_num), slot_config)
            deployed_instruments[int(slot_num)] = instrument

        # TODO: Apply routing configuration
        # This requires the routing API which varies by platform
        routing = config_dict.get('routing', [])
        if routing:
            print(f"Warning: Routing configuration not yet implemented ({len(routing)} connections specified)")

        print(f"Successfully deployed configuration to {ip}")
        return deployed_instruments

    except Exception as e:
        print(f"Error during deployment: {e}")
        raise

    finally:
        # Clean up connection (current API uses context manager)
        if hasattr(device, '__exit__'):
            device.__exit__(None, None, None)
