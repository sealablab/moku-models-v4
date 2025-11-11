"""
Moku Platform Models

Physical hardware models and routing abstractions for Moku devices.
Aligns with the 1st-party moku library conventions.

Core Abstraction:
    MokuConfig - THE central deployment model for this project

Device Operations:
    pull_config - Read configuration from running device
    push_config - Deploy configuration to device (overwrites existing)
"""

from moku_models.platforms.moku_go import MokuGoPlatform, MOKU_GO_PLATFORM
from moku_models.platforms.moku_lab import MokuLabPlatform, MOKU_LAB_PLATFORM
from moku_models.platforms.moku_pro import MokuProPlatform, MOKU_PRO_PLATFORM
from moku_models.platforms.moku_delta import MokuDeltaPlatform, MOKU_DELTA_PLATFORM
from moku_models.routing import MokuConnection, MokuConnectionList
from moku_models.moku_config import MokuConfig, SlotConfig, MokuPlatformConfig
from moku_models.discovery import MokuDeviceInfo, MokuDeviceCache
from moku_models.device import pull_config, push_config
from moku_models.validation import load_and_validate_config, validate_config_dict, fix_config_dict

__all__ = [
    # Core abstraction (use this!)
    'MokuConfig',
    'SlotConfig',

    # Platform specifications
    'MokuGoPlatform',
    'MOKU_GO_PLATFORM',
    'MokuLabPlatform',
    'MOKU_LAB_PLATFORM',
    'MokuProPlatform',
    'MOKU_PRO_PLATFORM',
    'MokuDeltaPlatform',
    'MOKU_DELTA_PLATFORM',

    # Routing
    'MokuConnection',
    'MokuConnectionList',

    # Device discovery
    'MokuDeviceInfo',
    'MokuDeviceCache',

    # Device operations
    'pull_config',
    'push_config',

    # Validation utilities
    'load_and_validate_config',
    'validate_config_dict',
    'fix_config_dict',

    # Backward compatibility (deprecated)
    'MokuPlatformConfig',
]
