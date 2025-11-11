# moku-models

Pydantic models for Moku device deployment, discovery, and configuration.

**Features:**
- Type-safe platform specifications (Moku:Go, Lab, Pro, Delta)
- MokuConfig deployment model with validation
- Device operations: pull/push configuration to/from hardware
- JSON serialization built-in via Pydantic

## Installation

```bash
# Install from local directory
pip install -e .

# Or with uv
uv pip install -e .
```

**Requirements:**
- `pydantic>=2.0` (required)
- `moku` (optional, only needed for device operations)

## Quick Start

### Define a Configuration

```python
from moku_models import (
    MokuConfig,
    SlotConfig,
    MokuConnection,
    MOKU_GO_PLATFORM
)

config = MokuConfig(
    platform=MOKU_GO_PLATFORM,
    slots={
        1: SlotConfig(
            instrument='CloudCompile',
            bitstream='my_instrument.tar',
            control_registers={
                0: 0xE0000000,  # FORGE control scheme
                1: 0x00000001,  # Application registers
            }
        ),
        2: SlotConfig(
            instrument='Oscilloscope',
            settings={'sample_rate': 125e6}
        )
    },
    routing=[
        MokuConnection(source='IN1', destination='Slot1InA'),
        MokuConnection(source='Slot1OutA', destination='OUT1'),
        MokuConnection(source='Slot1OutA', destination='Slot2InA'),
    ]
)

# Validate routing
errors = config.validate_routing()
if errors:
    print(f"Validation errors: {errors}")
```

### Save/Load Configuration

```python
import json

# Save to JSON
with open('config.json', 'w') as f:
    f.write(config.model_dump_json(indent=2))

# Load from JSON
with open('config.json') as f:
    config = MokuConfig.model_validate_json(f.read())
```

### Pull Configuration from Device

```python
from moku_models.device import pull_config

# Read current configuration from device
config = pull_config(ip='192.168.1.100')

# Save to file
config = pull_config(ip='192.168.1.100', save_to='current_config.json')

print(f"Device: {config['device_info']['platform']}")
print(f"Slots: {list(config['slots'].keys())}")
print(f"Control Registers: {config['control_registers']}")
```

### Push Configuration to Device

```python
from moku_models import MokuConfig
from moku_models.device import push_config

# Load configuration
with open('config.json') as f:
    config = MokuConfig.model_validate_json(f.read())

# Deploy to device (WARNING: overwrites existing config!)
push_config(
    ip='192.168.1.100',
    config=config,
    overwrite=True  # Required safety parameter
)
```

## Command-Line Tools

### Pull Config from Device

```bash
# Pull and display
python scripts/pull.py --ip 192.168.1.100

# Save to file
python scripts/pull.py --ip 192.168.1.100 --output config.json

# Specify platform
python scripts/pull.py --ip 192.168.1.100 --platform go
```

### Push Config to Device

```bash
# Deploy configuration (with confirmation)
python scripts/push.py --ip 192.168.1.100 --config deployment.json

# Skip confirmation
python scripts/push.py --ip 192.168.1.100 --config deployment.json --yes

# Specify platform
python scripts/push.py --ip 192.168.1.100 --config deployment.json --platform go
```

## Platform Specifications

Query platform capabilities:

```python
from moku_models import MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM

# Compare platforms
for platform in [MOKU_GO_PLATFORM, MOKU_LAB_PLATFORM, MOKU_PRO_PLATFORM]:
    print(f"{platform.name}: {platform.slots} slots @ {platform.clock_mhz} MHz")

# Check I/O specifications
platform = MOKU_GO_PLATFORM
in1 = platform.get_analog_input_by_id('IN1')
print(f"IN1: {in1.resolution_bits}-bit @ {in1.sample_rate_msa} MSa/s")

out1 = platform.get_analog_output_by_id('OUT1')
print(f"OUT1: ±{out1.voltage_range_vpp/2}V range")
```

## Available Platforms

| Platform | Slots | Analog I/O | Clock | DIO Pins |
|----------|-------|------------|-------|----------|
| Moku:Go | 2 | 2 IN / 2 OUT | 125 MHz | 16 |
| Moku:Lab | 2 | 2 IN / 2 OUT | 500 MHz | None |
| Moku:Pro | 4 | 4 IN / 4 OUT | 1.25 GHz | None |
| Moku:Delta | 3 | 8 IN / 8 OUT | 5 GHz | 32 |

## Documentation

- **CLAUDE.md** - Detailed architecture and integration guide
- **llms.txt** - Quick reference for LLMs
- **docs/MOKU_PLATFORM_SPECIFICATIONS.md** - Detailed hardware specs

## Development

```bash
# Format code
black moku_models/
ruff check moku_models/

# Run tests (when available)
pytest tests/
```

## License

MIT
