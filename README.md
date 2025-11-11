# moku-models

[![GitHub](https://img.shields.io/badge/github-sealablab%2Fmoku--models--v4-blue)](https://github.com/sealablab/moku-models-v4)

Pydantic models for Moku device deployment and configuration. Define hardware specs once, use everywhere: deployment scripts, validation, simulation.

**Repository:** https://github.com/sealablab/moku-models-v4

## Quick Start

### Pull Config from Device

```bash
# CLI
python scripts/pull.py --ip 192.168.1.100 --output config.json --validate

# Python API
from moku_models import pull_config

config = pull_config(ip='192.168.1.100', save_to='config.json')
print(f"Platform: {config['device_info']['platform']}")
print(f"Slots: {list(config['slots'].keys())}")
```

### Push Config to Device

```bash
# CLI (validates before pushing)
python scripts/push.py --ip 192.168.1.100 --config deployment.json

# Python API
from moku_models import MokuConfig, push_config

with open('config.json') as f:
    config = MokuConfig.model_validate_json(f.read())

push_config(ip='192.168.1.100', config=config, overwrite=True)
```

### Validate Config Files

```bash
# Works with YAML or JSON
python scripts/validate_moku_config.py deployment.yaml
python scripts/validate_moku_config.py config.json --verbose
```

## Installation

```bash
# Minimal (Pydantic only)
pip install -e .

# With device operations
pip install -e ".[device]"  # Adds moku + pyyaml
```

## Define Configuration

```python
from moku_models import MokuConfig, SlotConfig, MokuConnection, MOKU_GO_PLATFORM

config = MokuConfig(
    platform=MOKU_GO_PLATFORM,
    slots={
        1: SlotConfig(
            instrument='CloudCompile',
            bitstream='instrument.tar',
            control_registers={0: 0xE0000000}
        )
    },
    routing=[
        MokuConnection(source='IN1', destination='Slot1InA'),
        MokuConnection(source='Slot1OutA', destination='OUT1'),
    ]
)

# Validate
errors = config.validate_routing()
if not errors:
    print("✓ Valid configuration")
```

## Available Platforms

| Platform | Slots | Analog I/O | Clock | DIO | Constant |
|----------|-------|------------|-------|-----|----------|
| Moku:Go | 2 | 2 IN / 2 OUT | 125 MHz | 16 | `MOKU_GO_PLATFORM` |
| Moku:Lab | 2 | 2 IN / 2 OUT | 500 MHz | - | `MOKU_LAB_PLATFORM` |
| Moku:Pro | 4 | 4 IN / 4 OUT | 1.25 GHz | - | `MOKU_PRO_PLATFORM` |
| Moku:Delta | 3 | 8 IN / 8 OUT | 5 GHz | 32 | `MOKU_DELTA_PLATFORM` |

## Documentation

- **[CLAUDE.md](https://github.com/sealablab/moku-models-v4/blob/main/CLAUDE.md)** - Architecture and integration guide
- **[llms.txt](https://github.com/sealablab/moku-models-v4/blob/main/llms.txt)** - LLM quick reference
- **[Platform Specs](https://github.com/sealablab/moku-models-v4/blob/main/docs/MOKU_PLATFORM_SPECIFICATIONS.md)** - Detailed hardware specifications

## Project Structure

```
moku_models/
├── platforms/          # Platform definitions (Go, Lab, Pro, Delta)
├── moku_config.py      # MokuConfig, SlotConfig
├── routing.py          # MokuConnection, routing validation
├── validation.py       # Shared validation utilities
├── device/             # Device operations (pull/push)
└── discovery.py        # Device discovery models

scripts/
├── pull.py             # Pull config from device CLI
├── push.py             # Push config to device CLI
└── validate_moku_config.py  # Validate YAML/JSON files
```

## Contributing

This is a standalone library used by:
- [moku-instrument-forge](https://github.com/sealablab/moku-instrument-forge) - FPGA code generation
- [forge-v4-workspace](https://github.com/sealablab/forge-v4) - Development environment

See [CLAUDE.md](https://github.com/sealablab/moku-models-v4/blob/main/CLAUDE.md) for integration patterns.

## License

MIT
