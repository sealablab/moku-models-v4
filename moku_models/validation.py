"""
Shared validation utilities for MokuConfig.

Provides helpers for loading and validating configs from YAML/JSON files,
including platform reference fixup and non-Pydantic field cleanup.
"""

from pathlib import Path
from typing import Any, Dict, Tuple
import json

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

from moku_models import MokuConfig, MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM


# Platform lookup table
PLATFORM_MAP = {
    'moku_go': MOKU_GO_PLATFORM,
    'go': MOKU_GO_PLATFORM,
    'moku_lab': MOKU_LAB_PLATFORM,
    'lab': MOKU_LAB_PLATFORM,
    'moku_pro': MOKU_PRO_PLATFORM,
    'pro': MOKU_PRO_PLATFORM,
}


def fix_config_dict(data: Dict[str, Any]) -> Tuple[Dict[str, Any], list[str]]:
    """
    Fix common config dictionary issues before Pydantic validation.

    Handles:
    - Platform string → platform object conversion
    - Removal of non-Pydantic fields (description, physical_connections)
    - Cleanup of description fields in slots and routing

    Args:
        data: Raw config dictionary from YAML/JSON

    Returns:
        Tuple of (fixed_dict, warnings)

    Raises:
        ValueError: If platform string is unknown
    """
    warnings = []
    data = data.copy()  # Don't mutate input

    # Fix platform reference (YAML/JSON has string, model expects object)
    if 'platform' in data and isinstance(data['platform'], str):
        platform_name = data['platform'].lower()
        platform_obj = PLATFORM_MAP.get(platform_name)

        if platform_obj is None:
            raise ValueError(
                f"Unknown platform: {data['platform']}. "
                f"Valid options: {list(PLATFORM_MAP.keys())}"
            )

        data['platform'] = platform_obj
        warnings.append(f"Converted platform string '{data['platform']}' to platform object")

    # Remove non-Pydantic fields
    non_model_fields = ['description', 'physical_connections']
    for field in non_model_fields:
        if field in data:
            del data[field]
            warnings.append(f"Removed non-model field: {field}")

    # Remove description from slots
    if 'slots' in data:
        for slot_id, slot_config in data['slots'].items():
            if 'description' in slot_config:
                del slot_config['description']
                warnings.append(f"Removed description from slot {slot_id}")

    # Remove description from routing
    if 'routing' in data:
        for idx, route in enumerate(data['routing']):
            if 'description' in route:
                del route['description']
                warnings.append(f"Removed description from route {idx}")

    return data, warnings


def load_and_validate_config(
    file_path: Path,
    verbose: bool = False
) -> Tuple[bool, str, MokuConfig | None]:
    """
    Load and validate a MokuConfig from YAML or JSON file.

    Args:
        file_path: Path to YAML or JSON config file
        verbose: Show detailed warnings during fixup

    Returns:
        Tuple of (success, message, config_or_none)

    Example:
        >>> success, msg, config = load_and_validate_config(Path("deploy.yaml"))
        >>> if success:
        ...     print(f"Valid config: {config.platform.name}")
    """
    if not file_path.exists():
        return False, f"File not found: {file_path}", None

    try:
        # Load file based on extension
        suffix = file_path.suffix.lower()

        if suffix in ['.yaml', '.yml']:
            if not YAML_AVAILABLE:
                return False, "pyyaml not installed. Run: pip install pyyaml", None
            with open(file_path) as f:
                data = yaml.safe_load(f)

        elif suffix == '.json':
            with open(file_path) as f:
                data = json.load(f)
        else:
            return False, f"Unsupported file type: {suffix}. Use .yaml, .yml, or .json", None

        # Fix common issues
        data, warnings = fix_config_dict(data)

        if verbose and warnings:
            print("Fixup warnings:")
            for warning in warnings:
                print(f"  - {warning}")

        # Validate with Pydantic
        config = MokuConfig.from_dict(data)

        # Run routing validation
        routing_errors = config.validate_routing()
        if routing_errors:
            error_msg = "Routing validation failed:\n" + "\n".join(f"  - {err}" for err in routing_errors)
            return False, error_msg, None

        success_msg = (
            f"✓ Valid MokuConfig: {config.platform.name}, "
            f"{len(config.slots)} slots, {len(config.routing)} routes"
        )
        return True, success_msg, config

    except Exception as e:
        return False, f"✗ Validation failed: {e}", None


def validate_config_dict(data: Dict[str, Any]) -> Tuple[bool, str, MokuConfig | None]:
    """
    Validate a config dictionary (already loaded from JSON/YAML).

    Useful for validating configs before pushing to device.

    Args:
        data: Config dictionary

    Returns:
        Tuple of (success, message, config_or_none)
    """
    try:
        # Fix common issues
        data, _ = fix_config_dict(data)

        # Validate with Pydantic
        config = MokuConfig.from_dict(data)

        # Run routing validation
        routing_errors = config.validate_routing()
        if routing_errors:
            error_msg = "Routing validation failed:\n" + "\n".join(f"  - {err}" for err in routing_errors)
            return False, error_msg, None

        success_msg = (
            f"✓ Valid MokuConfig: {config.platform.name}, "
            f"{len(config.slots)} slots, {len(config.routing)} routes"
        )
        return True, success_msg, config

    except Exception as e:
        return False, f"✗ Validation failed: {e}", None
